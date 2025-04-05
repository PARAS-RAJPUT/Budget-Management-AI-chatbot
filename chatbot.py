import os
import google.generativeai as genai
from datetime import datetime
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

SECRET_KEY = os.getenv("SECRET_KEY")

class BudgetBot:
    def __init__(self):
        # Initialize the Gemini model
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.user_profile = {}
        self.conversation_history = []
        self.budget_info = {
            "monthly_income": None,
            "monthly_expenses": {},
            "savings_goals": [],
            "investment_preferences": None,
            "debt_info": {}
        }
    
    def save_profile(self, filename="user_profile.json"):
        """Save the user profile to a file"""
        with open(filename, 'w') as f:
            json.dump({"profile": self.user_profile, "budget_info": self.budget_info}, f)
        return "User profile saved successfully!"
    
    def load_profile(self, filename="user_profile.json"):
        """Load the user profile from a file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.user_profile = data.get("profile", {})
                self.budget_info = data.get("budget_info", {})
            return "User profile loaded successfully!"
        except FileNotFoundError:
            return "No profile found. Let's create a new one!"
    
    def update_profile(self, name=None, age=None, preferred_currency=None):
        """Update the user profile with basic information"""
        if name:
            self.user_profile["name"] = name
        if age:
            self.user_profile["age"] = age
        if preferred_currency:
            self.user_profile["preferred_currency"] = preferred_currency
        return "Profile updated successfully!"
    
    def set_budget_info(self, monthly_income=None, expenses=None, savings_goals=None, 
                       investment_preferences=None, debt_info=None):
        """Update the budget information"""
        if monthly_income:
            self.budget_info["monthly_income"] = monthly_income
        if expenses:
            self.budget_info["monthly_expenses"].update(expenses)
        if savings_goals:
            self.budget_info["savings_goals"] = savings_goals if isinstance(savings_goals, list) else [savings_goals]
        if investment_preferences:
            self.budget_info["investment_preferences"] = investment_preferences
        if debt_info:
            self.budget_info["debt_info"].update(debt_info)
        return "Budget information updated successfully!"
    
    def generate_budget_breakdown(self):
        """Generate a budget breakdown based on the current information"""
        if not self.budget_info["monthly_income"]:
            return "Please provide your monthly income first."
        
        prompt = f"""
        Create a detailed monthly budget breakdown for someone with a monthly income of {self.budget_info['monthly_income']} 
        in {self.user_profile.get('preferred_currency', 'USD')}.
        
        Current expenses: {json.dumps(self.budget_info['monthly_expenses'])}
        Savings goals: {', '.join(self.budget_info['savings_goals']) if self.budget_info['savings_goals'] else 'None specified'}
        Investment preferences: {self.budget_info['investment_preferences'] or 'Not specified'}
        Debt information: {json.dumps(self.budget_info['debt_info'])}
        
        Provide a breakdown of:
        1. Essential expenses (housing, utilities, groceries, etc.)
        2. Discretionary spending
        3. Savings allocation
        4. Debt payments
        5. Investment contributions
        
        For each category, suggest specific strategies to optimize spending and maximize savings.
        Include tips for reducing expenses and increasing savings.
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def suggest_savings_strategies(self):
        """Suggest savings strategies based on the user's situation"""
        prompt = f"""
        Suggest personalized savings strategies based on:
        Monthly income: {self.budget_info['monthly_income']}
        Current expenses: {json.dumps(self.budget_info['monthly_expenses'])}
        Savings goals: {', '.join(self.budget_info['savings_goals']) if self.budget_info['savings_goals'] else 'None specified'}
        
        Include:
        1. Recommended savings rate based on income
        2. Specific areas where expenses can be reduced
        3. High-yield savings account recommendations
        4. Automated savings strategies
        5. Emergency fund recommendations
        6. Tips for staying motivated to save
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def provide_investment_advice(self):
        """Provide investment advice based on the user's profile"""
        prompt = f"""
        Provide investment advice based on:
        Monthly income: {self.budget_info['monthly_income']}
        Investment preferences: {self.budget_info['investment_preferences'] or 'Not specified'}
        Savings goals: {', '.join(self.budget_info['savings_goals']) if self.budget_info['savings_goals'] else 'None specified'}
        
        Include:
        1. Recommended investment allocation
        2. Risk assessment
        3. Investment vehicle suggestions
        4. Tax-advantaged account recommendations
        5. Long-term investment strategies
        6. Common investment mistakes to avoid
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def suggest_debt_management(self):
        """Provide debt management strategies"""
        if not self.budget_info["debt_info"]:
            return "Please provide your debt information first."
        
        prompt = f"""
        Provide debt management strategies based on:
        Debt information: {json.dumps(self.budget_info['debt_info'])}
        Monthly income: {self.budget_info['monthly_income']}
        
        Include:
        1. Debt payoff prioritization
        2. Debt consolidation options
        3. Negotiation strategies with creditors
        4. Budget adjustments to accelerate debt payoff
        5. Emergency fund considerations
        6. Warning signs of problematic debt
        """
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def process_message(self, user_message):
        """Process user messages and generate appropriate responses"""
        # Add message to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Extract information from user message
        if "income" in user_message.lower():
            income_match = re.search(r"(\d+)\s*(?:k|thousand|k\/month|per month)", user_message.lower())
            if income_match:
                self.budget_info["monthly_income"] = int(income_match.group(1)) * 1000
        
        # Generate response based on message content
        if "budget" in user_message.lower() or "breakdown" in user_message.lower():
            response = self.generate_budget_breakdown()
        elif "save" in user_message.lower() or "savings" in user_message.lower():
            response = self.suggest_savings_strategies()
        elif "invest" in user_message.lower() or "investment" in user_message.lower():
            response = self.provide_investment_advice()
        elif "debt" in user_message.lower():
            response = self.suggest_debt_management()
        else:
            # Default response for general queries
            prompt = f"""
            You are a helpful budget assistant. The user has provided the following information:
            Monthly income: {self.budget_info['monthly_income']}
            Current expenses: {json.dumps(self.budget_info['monthly_expenses'])}
            Savings goals: {', '.join(self.budget_info['savings_goals']) if self.budget_info['savings_goals'] else 'None specified'}
            
            Please provide a helpful response to: {user_message}
            
            Focus on:
            1. Budget management
            2. Savings strategies
            3. Investment opportunities
            4. Debt management
            5. Financial planning
            """
            
            response = self.model.generate_content(prompt)
            response = response.text
        
        # Add response to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response

def main():
    bot = BudgetBot()
    print("Budget Assistant initialized. Type 'quit' to exit.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        
        response = bot.process_message(user_input)
        print("Assistant:", response)

if __name__ == "__main__":
    main()