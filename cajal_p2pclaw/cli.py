import argparse
from .chat import chat
from .model import load_model

def main():
    parser = argparse.ArgumentParser(
        prog="cajal",
        description="CAJAL-4B — P2PCLAW Scientific Intelligence CLI"
    )
    parser.add_argument("prompt", nargs="?", help="Prompt to send to CAJAL")
    parser.add_argument("--model", default="Agnuxo/CAJAL-4B-P2PCLAW", help="Model ID")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive chat mode")
    parser.add_argument("--system", help="Custom system prompt")
    parser.add_argument("--max-tokens", type=int, default=512, help="Max new tokens")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature")
    
    args = parser.parse_args()
    
    if args.interactive or not args.prompt:
        print("🧠 CAJAL Interactive Chat")
        print(f"Model: {args.model}")
        print("Type 'exit' or 'quit' to leave.\n")
        
        model = load_model(args.model)
        
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in ("exit", "quit", "q"):
                    break
                if not user_input:
                    continue
                
                response = model.chat(
                    user_input,
                    max_new_tokens=args.max_tokens,
                    temperature=args.temperature,
                    system_prompt=args.system,
                )
                print(f"\nCAJAL: {response}\n")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                break
    else:
        response = chat(
            args.prompt,
            model_id=args.model,
            max_new_tokens=args.max_tokens,
            temperature=args.temperature,
            system_prompt=args.system,
        )
        print(response)

if __name__ == "__main__":
    main()
