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
    temperature: float = 0,
    top_p: float = 0.8,
    max_seq_len: int = 8000,
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
        content=(Utils.Generic.ingestion_functions.model_context_ingestion(file_path='./Model_context/request_classification_context.txt', context_type='request_classification')),
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