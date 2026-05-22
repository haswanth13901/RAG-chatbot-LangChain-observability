import httpx, uuid, sys

BASE_URL   = "http://localhost:8000"
SESSION_ID = str(uuid.uuid4())[:8]

CYAN  = "\033[96m"
GREEN = "\033[92m"
AMBER = "\033[93m"
GRAY  = "\033[90m"
RED   = "\033[91m"
BOLD  = "\033[1m"
RESET = "\033[0m"


def print_header(chat_model: str = ""):
    print(f"\n{BOLD}{'─'*60}{RESET}")
    print(f"{BOLD}  RewardPlus RAG Chatbot{RESET}")
    if chat_model:
        print(f"{BOLD}  Model  : {chat_model}{RESET}")
    print(f"{BOLD}  Session: {SESSION_ID}{RESET}")
    print(f"{BOLD}{'─'*60}{RESET}\n")


def check_server() -> bool:
    try:
        h = httpx.get(f"{BASE_URL}/health", timeout=10).json()

        chat_model  = h.get("chat_model", "unknown")
        embed_model = h.get("embed_model", "unknown")
        groq_key    = h.get("groq_key", False)
        google_key  = h.get("google_key", False)
        chunks      = h.get("chunks_indexed", 0)
        sessions    = h.get("active_sessions", 0)

        print(f"{GRAY}  Server     : {GREEN}online{RESET}")
        print(f"{GRAY}  Chat model : {chat_model}{RESET}")
        print(f"{GRAY}  Embed model: {embed_model}{RESET}")
        print(f"{GRAY}  Chunks     : {chunks} policy chunks indexed{RESET}")
        print(f"{GRAY}  Sessions   : {sessions} active{RESET}")
        print(f"{GRAY}  Groq key   : {GREEN+'loaded'+RESET if groq_key   else RED+'MISSING'+RESET}")
        print(f"{GRAY}  Gemini key : {GREEN+'loaded'+RESET if google_key else RED+'MISSING'+RESET}")
        print()

        if chunks == 0:
            print(f"{RED}  WARNING: 0 chunks indexed — check your Docs/ folder{RESET}\n")

        if not groq_key and not google_key:
            print(f"{RED}  ERROR: No API keys loaded — add them to .env{RESET}\n")
            return False

        return True
    except Exception as e:
        print(f"{RED}Server not reachable: {e}{RESET}")
        print("Start first:\n  uvicorn main:app --reload --port 8000\n")
        return False


def chat(message: str) -> dict:
    r = httpx.post(
        f"{BASE_URL}/chat",
        json={"session_id": SESSION_ID, "message": message},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def transact(txn_type: str, amount: float,
             category: str = None, merchant: str = None) -> dict:
    r = httpx.post(
        f"{BASE_URL}/transaction/reward",
        json={
            "session_id":     SESSION_ID,
            "transaction_id": f"txn_{uuid.uuid4().hex[:8]}",
            "user_id":        "test_user_001",
            "type":           txn_type,
            "amount":         amount,
            "category":       category,
            "merchant":       merchant,
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def show_chat(question: str, result: dict):
    print(f"{CYAN}You:{RESET} {question}")
    print(f"{GREEN}RewardBot:{RESET} {result['answer']}")
    if result.get("sources"):
        print(f"{GRAY}  Sources: {', '.join(result['sources'])}{RESET}")
    print()


def show_txn(label: str, result: dict):
    print(f"{AMBER}{BOLD}Transaction: {label}{RESET}")
    print(f"  Points    : {BOLD}{result['points_earned']:,}{RESET}")
    print(f"  Multiplier: {result['multiplier_applied']}x  ({result['reward_tier']})")
    print(f"{GREEN}RewardBot:{RESET} {result['chatbot_explanation']}")
    if result.get("sources"):
        print(f"{GRAY}  Sources: {', '.join(result['sources'])}{RESET}")
    print()


def show_section(title: str):
    print(f"{BOLD}{'─'*60}{RESET}")
    print(f"{BOLD}  {title}{RESET}")
    print(f"{BOLD}{'─'*60}{RESET}\n")


def run_demo():
    if not check_server():
        sys.exit(1)

    h = httpx.get(f"{BASE_URL}/health", timeout=10).json()
    print_header(h.get("chat_model", ""))

    show_section("Scene 1 — Onboarding questions")
    show_chat("How do I earn points in the RewardPlus program?",
              chat("How do I earn points in the RewardPlus program?"))
    show_chat("Which spending category gives the most points per dollar?",
              chat("Which spending category gives the most points per dollar?"))

    show_section("Scene 2 — All transaction types")
    show_txn("$120 dining at Sushi Palace",
             transact("purchase", 120.00, "dining", "Sushi Palace"))
    show_txn("$45 groceries at Whole Foods",
             transact("purchase", 45.00, "groceries", "Whole Foods"))
    show_txn("$850 flight booking",
             transact("purchase", 850.00, "travel", "Delta Airlines"))
    show_txn("$200 bank transfer",
             transact("transfer", 200.00))
    show_txn("$89 electricity bill",
             transact("bill_payment", 89.00, "utilities", "City Power"))
    show_txn("$14.99 Netflix subscription",
             transact("subscription", 14.99, "streaming", "Netflix"))
    show_txn("Referral bonus",
             transact("referral", 0))

    show_section("Scene 3 — Conversational follow-ups (memory test)")
    show_chat("You mentioned travel gets 5x — is that for hotels too?",
              chat("You mentioned travel gets 5x — is that for hotels too?"))
    show_chat("How long before my points expire?",
              chat("How long before my points expire?"))
    show_chat("What if I don't use my account for 13 months?",
              chat("What if I don't use my account for 13 months?"))
    show_chat("Can I transfer points to my sister?",
              chat("Can I transfer points to my sister?"))

    show_section("Scene 4 — Policy and legal questions")
    show_chat("How do I dispute incorrect points and how long does it take?",
              chat("How do I dispute incorrect points and how long does it take?"))
    show_chat("Can the company change the earning rates without notice?",
              chat("Can the company change the earning rates without notice?"))

    print(f"{BOLD}{'─'*60}{RESET}")
    print(f"Demo complete. Run with --interactive for live REPL mode.\n")


def run_interactive():
    if not check_server():
        sys.exit(1)
    h = httpx.get(f"{BASE_URL}/health", timeout=10).json()
    print_header(h.get("chat_model", ""))
    print(f"Type your question and press Enter. Type {BOLD}quit{RESET} to exit.\n")
    while True:
        try:
            q = input(f"{CYAN}You: {RESET}").strip()
            if not q:
                continue
            if q.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            result = chat(q)
            print(f"{GREEN}RewardBot:{RESET} {result['answer']}")
            if result.get("sources"):
                print(f"{GRAY}  [{', '.join(result['sources'])}]{RESET}")
            print()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except httpx.HTTPStatusError as e:
            print(f"{RED}API error {e.response.status_code}: {e.response.text}{RESET}\n")
        except Exception as e:
            print(f"{RED}Error: {e}{RESET}\n")


if __name__ == "__main__":
    if "--interactive" in sys.argv:
        run_interactive()
    else:
        run_demo()