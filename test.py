# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# top-level folder for each specific model found within the models/ directory at
# the top-level of this source tree.

# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed in accordance with the terms of the Llama 3 Community License Agreement.

from typing import Optional

import fire

from llama_models.llama3.api.datatypes import RawMessage, StopReason

from llama_models.llama3.reference_impl.generation import Llama

import pandas as pd

import Utils.Generic.ingestion_functions

import os
os.environ["MASTER_ADDR"] = "127.0.0.1"  # Loopback address for single node
os.environ["MASTER_PORT"] = "29500"      # Arbitrary free port
os.environ["WORLD_SIZE"] = "1"           # Total number of processes
os.environ["RANK"] = "0"                 # Current process rank
os.environ["LOCAL_RANK"] = "0"           # Current process rank within the node

def run_main(
    ckpt_dir: str = "/home/nassim/.llama/checkpoints/Llama3.1-8B-Instruct",
    temperature: float = 0.2,
    top_p: float = 0.8,
    max_seq_len: int = 512,
    max_batch_size: int = 4,
    max_gen_len: Optional[int] = None,
    model_parallel_size: Optional[int] = None,
):
    """
    Examples to run with the models finetuned for chat. Prompts correspond of chat
    turns between the user and assistant with the final one always being the user.

    An optional system prompt at the beginning to control how the model should respond
    is also supported.

    `max_gen_len` is optional because finetuned models are able to stop generations naturally.
    """
    conversation_df = pd.DataFrame(columns=["user_prompt", "response"])

    generator = Llama.build(
        ckpt_dir=ckpt_dir,
        max_seq_len=max_seq_len,
        max_batch_size=max_batch_size,
        model_parallel_size=model_parallel_size,
    )

    system_prompt = RawMessage(
        role="system",
        content=(
            "You are a helpful assistant. "
            "You will classify the given text as either 'quote_request' or 'other'. "
            "A 'quote_request' is a document that a seller provides to a buyer to offer goods or services at a stated price, under specified conditions. 'quote_request' are used to let a potential buyer know how much goods or services will cost before they commit to the purchase"
            "A 'quote_request' occurs when the user expresses interest in buying a product or service."
            "its important to note that 'quote_request' has a strict definition of being able to provide a specific service or specific product at price. it is not general questions about a product or service"
            "for a 'quote_request' we must be able to determine what is the exact item or service they are looking to purchase."
            "All other queries are classified as 'other'. "
            "Only respond with one of these labels: 'quote_request' or 'other'. "
            "Examples: "
            "1. User: 'What is the price for bulk orders of drill bits?' → quote_request "
            "2. User: 'Can you explain your warranty policy?' → other "
            "3. User: 'What are the terms and conditions for bulk purchases?' → other"
            "4. User: 'Can I schedule a call with your sales team?' → other"
            "5. User: 'How do I download an invoice for my purchase?' → other"
            "6. User: 'Do you offer any discounts for bulk purchases?' → other"
            "7. User: 'What is the minimum order quantity for your products?' → other"
            "8. User: 'Can your product be leased instead of purchased?' → other"
            "9. User: 'How do you calculate shipping costs for bulk orders?' → other"
            "10. User: 'Do you offer volume pricing for wholesale buyers?' → other"
            "Classify the following query."
        ),
    )

    user_inputs = Utils.Generic.ingestion_functions.user_text_prompt_ingestion('./samples/quote_request_samples.txt')



    for input in user_inputs:


        dialog =[
            system_prompt,
            RawMessage(role='user',content=input)
        ]

        result = generator.chat_completion(
            dialog,
            max_gen_len=max_gen_len,
            temperature=temperature,
            top_p=top_p,
        )

        for msg in dialog:
            print(f"{msg.role.capitalize()}: {msg.content}\n")
        
        user_prompt = dialog[1].content
        response = result.generation.content 
        conversation_df = pd.concat(
            [conversation_df, pd.DataFrame({"user_prompt": [user_prompt], "response": [response]})],
            ignore_index=True,
        )

        out_message = result.generation
        print(f"> {out_message.role.capitalize()}: {out_message.content}")
        print("\n==================================\n")

        conversation_df.to_csv("conversation_log.csv", index=False)
        print("Conversation logged to conversation_log.csv")


def main():
    fire.Fire(run_main)


if __name__ == "__main__":
    main()