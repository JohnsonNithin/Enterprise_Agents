leave_policy = "Employees receive 20 annual leave days."


def answer_questions(question)->str:
    """Returns the supported policy for the given question or a safe refusal."""
    if "leave" in question.lower():
        return leave_policy
    else:
        return "I do not know based on the available policies."
    
def main()->None:
    question=input("Ask a policy question: ")
    answer=answer_questions(question)
    print(answer)

if __name__=="__main__":
    main()  
