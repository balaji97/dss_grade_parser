import argparse
import pdftotext

def getWords(text):
    wordsInText = []
    lines = text.split("\n")
    for line in lines:
        words = line.split(" ")
        for word in words:
            extractedWord = word.strip()
            if(extractedWord != ""):
                wordsInText.append(extractedWord)
    
    return wordsInText
    
def stripMetaData(gradeCard):
    lines = gradeCard.split("\n")
    strippedGradeCard = []
    
    name, roll = getNameAndRoll(gradeCard)
    
    for line in lines:
        if "National Institute of Technology, Calicut" in line:
            continue
        elif name in line and roll in line:
            continue
        elif "Sl No." in line and "Code" in line and "Course" in line and "Credits" in line and "Grade" in line and "Result" in line:
            continue
        elif "Page No" in line:
            continue
        elif "ActiveReports Evaluation" in line:
            continue
        else:
            strippedGradeCard.append(line)
    
    return ("\n".join(strippedGradeCard)).rstrip()
    
def isValidGradeCard(gradeCard):
    if("National Institute of Technology, Calicut" in gradeCard and "ActiveReports Evaluation" in gradeCard):
        return True
    else:
        return False
    
def getNameAndRoll(gradeCard):
    nameAndRoll = getWords(gradeCard.split("\n")[1])
    return " ".join(nameAndRoll[:-1]), nameAndRoll[-1]
    
def getGradeCardData(path):
    with open(path, 'rb') as file:
        gradeCard = "".join(pdftotext.PDF(file))
        
        if(not isValidGradeCard(gradeCard)):
            return "Not a valid Grade Card"

        name, roll = getNameAndRoll(gradeCard)
        strippedGradeCard = stripMetaData(gradeCard)
    
    return name, roll, strippedGradeCard 
    
def getArgumentParser():
    argumentParser = argparse.ArgumentParser()
    argumentParser.add_argument('-p', '--path', help = 'Path to the GradeSheet to be parsed', type = str)
    return argumentParser

def getPathArgument(argumentParser):
    return argumentParser.parse_args().path

def getDividedBySemester(parsedGradeCard):
    gradesBySemester = []
    linesOfSemester = []
    
    numberOfLines = len(parsedGradeCard.split("\n"))
    
    for index, line in enumerate(parsedGradeCard.split("\n")):
        if("Semester :" in line):
            if(len(linesOfSemester) > 0):
                gradesBySemester.append("\n".join(linesOfSemester))
                linesOfSemester = []
        else:
            linesOfSemester.append(line)
            if(index == numberOfLines - 1):
                gradesBySemester.append("\n".join(linesOfSemester))
    
    return gradesBySemester
    
def contributesToCGPA(grade):
    if(grade == "P"):
        return False
    else:
        return True

def getGradePoint(grade):
    if(grade == "S"):
        return 10
    elif(grade == "A"):
        return 9
    elif(grade == "B"):
        return 8
    elif(grade == "C"):
        return 7
    elif(grade == "D"):
        return 6
    elif(grade == "E"):
        return 5
    elif(grade == "R"):
        return 4
    else:
        return 0
    
def getGradesBySemester(parsedGradeCard):
    gradesBySemester = getDividedBySemester(parsedGradeCard)
    
    listOfCredits = []
    listOfSGPA = []
    otCredits = 0
    
    for semesterGrades in gradesBySemester:
        listOfGrades = semesterGrades.split("\n")
        semesterCredits = 0
        sgpa = 0
        for gradeLine in listOfGrades:
            lineWords = getWords(gradeLine)
            
            credits = int(lineWords[-3])
            grade = lineWords[-2]
            
            if(contributesToCGPA(grade)):
                semesterCredits += credits
                sgpa += credits*getGradePoint(grade)
            else:
                otCredits += 1
                
        sgpa = sgpa/semesterCredits
        listOfCredits.append(semesterCredits)
        listOfSGPA.append(sgpa)
    
    return listOfCredits, listOfSGPA, otCredits
    
def getCGPA(listOfCredits, listOfSGPA):
    cgpa = 0
    credits = 0
    
    for i in range(len(listOfSGPA)):
        credits += listOfCredits[i]
        cgpa += listOfCredits[i]*listOfSGPA[i]
    
    cgpa /= credits
    return credits, cgpa
    
if __name__ == '__main__':
    
    name, roll, parsedGradeCard = getGradeCardData(getPathArgument(getArgumentParser()))
    
    print("Name: " + name)
    print("Roll: " + roll)
    
    listOfCredits, listOfSGPA, otCredits = getGradesBySemester(parsedGradeCard)
    
    print("Semester\tCredits\tSGPA\n")
    numberOfSemesters = len(listOfSGPA)
    
    for i in range(numberOfSemesters):
        semester = i+1
        print(str(semester) + "\t" + str(listOfCredits[i]) + "\t" + str(listOfSGPA[i]))
    
    credits, cgpa = getCGPA(listOfCredits, listOfSGPA)
    
    print("Number of non OT credits: " + str(credits))
    print("Number of OT Credits: " + str(otCredits))
    print("Total number of Credits: " + str(credits + otCredits))
    print("CGPA: " + str(cgpa))