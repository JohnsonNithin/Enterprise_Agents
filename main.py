# this is like a baseline for your understanding pythonic foundations .

from dataclasses import dataclass

@dataclass(frozen=True) # frozen is true bcs approved policy should not be changed if the program is running 
class policy:
    """Blue print of manually created Policy class for the Enterprise Agent"""
    topic:str
    answer:str

POLICIES:list[policy]=[
    
    policy(topic="leave",
           answer="The employee has 20 days of leave annually. The employee can take leave at any time without penalty. The employee must take leave on the same day every year. The employee cannot take more than 20 days of leave in a year."),
    policy(topic="sick",
           answer="The employee has 10 days of sick leave annualy."),
    policy(topic="personal",
           answer="The employee has 100 days of personal leave annually. The employee can take personal leave at any time without penalty. The employee must take personal leave on the same day every year. The employee cannot take more than 30 days of personal leave in a year."),
    policy(topic="Travel",
           answer="Travel claims must be submitted within 50 days.")
    ]

def answer_question(question:str)->str:
    """This function is used to answer the question asked by the user"""
    for policy in POLICIES:
        if policy.topic.lower() in question.lower():
            return policy.answer
    return "I don't know the answer to that question"


def main()->None:
    """This function is the main function of the Enterprise Agent"""
    print("Enterprise Agent is running")
    question = input("Enter your question: ")
    answer = answer_question(question)
    print(f"Answer: {answer}")


if __name__=="__main__":
    main()