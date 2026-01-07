import google.generativeai as genai
from core.config import config

class GeminiGenerator:
    def __init__(self):
        #hardcoded key
        self.key=config.GOOGLE_API_KEY
        genai.configure(api_key=self.key)
        self.model=genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_answer(self, context: list, user_question: str)->str:
        #formatting context
        formatted_context="\n".join([f"<doc>{doc.strip()}</doc>" for doc in context])

        #prompt
        prompt=f"""
        You are a specialized AI Assistant. Your knowledge is strictly limited to the provided context.

        <context>
        {formatted_context}
        </context>

        <question>
        {user_question}
        </question>

        <constraints>
        1. NO META-TALK: Do not say "According to the documents" or "In the provided text". Just state the facts directly if they are sufficient.
        2. SCOPE CHECK: If the user asks for a general definition  and your context ONLY has a specific technical definition in some context, DO NOT answer as if that is the universal definition.
           - INSTEAD: State clearly that you dont know the answer since it is out of the scope of the database.
        3. If the answer is not in the context, strictly reply: "I'm sorry, but that information is not available in my current database."
        4. Maintain a professional, direct tone.
        </constraints>
        """
        try:
            response=self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating answer: {str(e)}"

gemini_generator=GeminiGenerator()