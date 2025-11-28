import asyncio  
from google.adk.runners import Runner  
from google.adk.sessions import DatabaseSessionService  
from google.genai import types
from dotenv import load_dotenv  
load_dotenv(override=True) 
   
from agent import root_agent
  
async def run_agent(query: str) -> str:  
    """  
    Run the agent programmatically with a query.  
      
    Args:  
        query: The user's question  
          
    Returns:  
        The agent's final response text  
    """   
    
    # you need to have setted a database working in your machine in order to use DatabaseSessionService

    # setup postgres with docker
    # docker build -t postgres-agent -f 06_sdk_agents_operations/Dockerfile 06_sdk_agents_operations/
    # docker run -d -p 5432:5432 --name postgres-agent postgres-agent
    
    database_url = "postgresql://agent_user:agent_password@localhost:5432/agent_sessions"
    session_service = DatabaseSessionService(db_url=database_url)
      

    APP_NAME = "course_assistant"  
    USER_ID = "user_1"  
    session = await session_service.create_session(  
        app_name=APP_NAME,   
        user_id=USER_ID  
    )  
      
    runner = Runner(  
        agent=root_agent,  
        app_name=APP_NAME,  
        session_service=session_service  
    )  
      
    user_content = types.Content(  
        role='user',   
        parts=[types.Part(text=query)]  
    )  
      
 
    final_response = ""  
    async for event in runner.run_async(  
        user_id=USER_ID,  
        session_id=session.id,  
        new_message=user_content  
    ):  
        if event.is_final_response() and event.content and event.content.parts:  
            final_response = event.content.parts[0].text  
      
    return final_response  
  

async def main():  
    response = await run_agent("what are all the avaialble courses for the Data and Web Science program?")  
    print(f"Agent response: {response}")  
  
if __name__ == "__main__":  
    asyncio.run(main())