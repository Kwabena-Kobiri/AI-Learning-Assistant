# app/services/conversational_chain.py
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from app.services.vector_retriever import VectorRetriever
from app.services.chat_history import ChatHistory
from app.utils.callback_handler import WebSocketStreamingCallbackHandler
from langchain_openai import ChatOpenAI
from app.config import Config
import logging

class ConversationalChain:
    def __init__(self, websocket):
        self.websocket = websocket
        self.llm = ChatOpenAI(
            model="gpt-4o", temperature=0, api_key=Config.OPENAI_API_KEY
        )
        self.chain_llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=Config.OPENAI_API_KEY, streaming=True, callbacks=[WebSocketStreamingCallbackHandler(websocket)])
        self.vector_retriever = VectorRetriever()
        self.chat_history = ChatHistory()

    def create_conversational_chain(self) -> str:
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question, "
            "formulate a standalone question which can be understood without the chat history."
        )

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        history_aware_retriever = create_history_aware_retriever(
            self.llm, self.vector_retriever.get_retriever(), contextualize_q_prompt
        )

        system_prompt = (
            "You are an assistant for exam preparation tasks. "
            "You offer assistance to students who wish to prepare for their exams. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. If the answer cannot be found in the provided context, "
            "you may rely on your general knowledge to provide an answer. "
            "If you are not sure about the answer, provide the closest possible answer "
            "but state emphatically that you are not sure about it. "
            "Make sure to provide full complete answers, "
            "add explanations and examples where applicable, and make no assumptions. "
            "DO NOT provide an answer if the query is unrelated to exam preparation, "
            "let the student know that it does not fall within your scope of expertise. "
            "Give your response in markdown. "
            "\n\n"
            "{context}"
        )


        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        question_answer_chain = create_stuff_documents_chain(self.chain_llm, qa_prompt)

        rag_chain = create_retrieval_chain(
            history_aware_retriever, question_answer_chain
        )
        
        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            self.chat_history.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
        logging.info("Returning Conversational RAG Chain...")
        #print("Returning Conversational RAG Chain...")
        return conversational_rag_chain

    
    async def handle_user_query(self, session_id: str, user_query: str):
        chat_history = self.chat_history.get_session_history(session_id)
        
        response = []
        async for response_chunk in self.create_conversational_chain().astream(
            {"input": user_query},
             config={
                 "configurable": {"session_id": session_id}
             }
            ):
            response.append(response_chunk)
        # print("Sent all chunks")   
        chat_history.add_user_message(user_query)
        chat_history.add_ai_message(''.join(item['answer'] for item in response if 'answer' in item))
        logging.info("Sent all chunks and added response to ChatHistory...")
        print("Sent all chunks and added response to ChatHistory...")    