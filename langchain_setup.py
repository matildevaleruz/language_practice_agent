import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


# LangChain setup
llm = ChatOpenAI(  # openrouter uses the same protocol, we can still use any llm
    model=os.environ.get('OPENROUTER_MODEL', 'mistralai/mistral-7b-instruct:free'),
    base_url=os.environ.get('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1'),
    api_key=os.environ.get('OPENROUTER_API_KEY'),
    temperature=0.5,
    timeout=30.0
)

# prompt definition
conversation_prompt_template = PromptTemplate(
    input_variables=['language', 'level', 'focus', 'context', 'history', 'text'],
    template="""You are having a casual conversation in {language} at CEFR level {level}. 

**Setting:** {context}
**Conversation focus:** {focus}

Speak naturally as a person in this situation would. 
Keep responses concise (1-2 sentences typically). 
Use simple language appropriate for the user's level. 
Ask relevant follow-up questions to continue the conversation naturally. 
Do not provide explanations, teaching comments, or suggestions in parentheses - just respond as your character would.

Current conversation:
{history}
User: {text}
Assistant:"""
)

feedback_prompt_template = PromptTemplate(
    input_variables=['language', 'level', 'focus', 'context','conversation_json'],
    template="""You are a friendly and encouraging {language} teacher. 
The user has just finished a conversation at CEFR level {level}. Setting: {context}. Conversation focus: {focus}.

Analyze the provided conversation and return a single JSON object with feedback.
The JSON object must contain four keys: "corrections", "strengths", "weaknesses", and "recommendations".
- "corrections" should be a list of objects, where each object has "turn_index", "user_text", "corrected_text", and "explanation".
- "strengths", "weaknesses", and "recommendations" should be lists of strings.

Guidelines for feedback:
1. Corrections: List only the most important errors. Do not correct every missing punctuation unless it affects meaning. Focus on errors in vocabulary, grammar, and sentence structure.
2. Strengths: Mention 2-3 things the user did well, such as using new vocabulary, correct grammar structures, or natural expressions.
3. Weaknesses: Point out 2-3 areas for improvement, focusing on recurring errors or important aspects for their level. Be constructive and encouraging.
4. Recommendations: Provide 2-3 specific, actionable recommendations for improvement. Avoid vague advice.

Do not include any text or formatting outside of the JSON object itself.

Conversation:
{conversation_json}
"""
)

# chains
conversation_chain = conversation_prompt_template | llm | StrOutputParser()
feedback_chain = feedback_prompt_template | llm | StrOutputParser()
