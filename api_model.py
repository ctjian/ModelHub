import json
import sys
import copy
from abc import ABC

from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from config.api_keys import *


class APIModel(ABC):
    def __init__(self, api_key="EMPTY", host_url="http://192.168.50.71:8000/v1", model: str = "qwen7b",
                 temperature: float = 0.1, max_tokens: int = 2048, top_p: float = 0.9, **more_params):
        self.api_key = api_key
        self.host_url = host_url
        self.params = {
            'model': model,
            'temperature': temperature,
            'top_p': top_p,
            'max_tokens': max_tokens, 
            **more_params
        }
        self.conversation_history = []  # Used to store multi-turn conversation history

        # Initialize OpenAI client with api_key and base_url
        self.client = OpenAI(api_key=self.api_key, base_url=self.host_url)


    def request(self, query: str, multi_turns=False, model=None) -> str:
        if not multi_turns:
            self.reset_conversation()

        params = copy.deepcopy(self.params)
        if model is not None:
            params['model'] = model

        # Add current user input to conversation history
        self.conversation_history.append({"role": "user", "content": query})

        # Send request to get completion
        success = False
        try_count = 0
        while not success:
            if try_count >= 3:
                print("Error: failed to get response from API after 3 attempts.")
                return ''
            try:

                completion = self.client.chat.completions.create(
                    messages=self.conversation_history,  # Send conversation history
                    timeout=120,  # Timeout in seconds
                    **params
                )
                success = True
            except Exception as e:
                print(f"Warning: error during API request: {e}")
                pass

            try_count += 1

        resp = completion.choices[0].message.content
        # Remove special tokens
        resp = resp.replace("<|im_end|>", "").replace("<|im_start|>", "").strip()

        # Add model's reply to conversation history
        self.conversation_history.append({"role": "assistant", "content": resp})
        return resp
    
    def request_stream(self, query: str, multi_turns=False, model=None, stop_event=None):
        global stop_streaming
        if not multi_turns:
            self.reset_conversation()

        params = copy.deepcopy(self.params)
        if model is not None:
            params['model'] = model

        # Add current user input to conversation history
        self.conversation_history.append({"role": "user", "content": query})

        try:
            # Stream completion response
            response = self.client.chat.completions.create(
                messages=self.conversation_history,
                stream=True,  # Enable streaming
                timeout=120,
                **params
            )
            # Process the streamed response
            for chunk in response:
                if stop_event is not None and stop_event.is_set():
                    response.close()
                    print("Streaming stopped by user.")
                yield chunk.choices[0].delta.content
            
        except Exception as e:
            print(f"Warning: error during streaming API request: {e}")
            yield "Requset Failed：" + str(e)


    def request_in_parallel(self, queries, max_workers=128):
        """
        Execute multiple queries in parallel using a thread pool.

        :param queries: A list of strings, where each string is a query to the model.
        :param max_workers: Maximum number of threads to use for concurrent execution.
        :return: A list of results for each query.
        """
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_query = {executor.submit(self.request, query): query for query in queries}

            for future in as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # print(f"Error during request for query '{query}': {e}")
                    results.append('')

        return results

    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []


# Factory function to create the appropriate client
def create_llm_client(api_key="EMPTY", host_url="http://192.168.50.71:8000/v1", model="qwen7b", max_tokens=2048,
                      temperature=0.1, top_p=0.5, **more_params):
    return APIModel(
        api_key=api_key,
        host_url=host_url,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        **more_params
    )


# Example usage:

if __name__ == "__main__":
    from config.api_keys import *
    gn_llm = APIModel(Sili_APIKEY, Sili_BASE_URL, "01-ai/Yi-1.5-9B-Chat-16K")
    # import time
    # start = time.time()
    # resps = gn_llm.request_in_parallel(["你是？"] * 1)
    # print(time.time() - start)
    # for r in resps:
    #     print("#" * 50)
    #     print(r)
    # resp = gn_llm.request_stream("你是？")
    # for r in resp:
    #     print(r)
