import sys
from pathlib import Path

# Add project root to sys.path so 'src' resolves regardless of how the script is invoked
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.matcher import ProtocolMatcher


def run_cli():
    matcher = ProtocolMatcher()
    print("=" * 70)
    print("NAM Protocol Engine - Regulatory Alternative Matcher")
    print("Type a query (or 'exit' / 'quit' to stop)")
    print("=" * 70)

    while True:
        try:
            query = input("\nEnter animal test or toxicity endpoint: ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit", "q"):
                print("Exiting engine.")
                break

            result = matcher.find_alternative(query)
            print("-" * 70)
            if result.matched and result.protocol:
                proto = result.protocol
                print(f"MATCH FOUND: {proto.protocol_name}")
                print(f"Target Tissue:       {proto.endpoint.target_tissue}")
                print(f"Historical Test:     {proto.endpoint.historical_animal_test}")
                print(f"Category:            {proto.technology_category}")
                print(f"Status:              {proto.regulatory_status}")
                print(f"\nContext of Use:\n  {proto.context_of_use}")
                print(
                    f"\nPrimary Citation:\n  {proto.citations[0].standard_body} - {proto.citations[0].guideline_id} ({proto.citations[0].section_reference})"
                )
            else:
                print("NO EXACT MATCH FOUND")
                print(f"Recommendation: {result.recommendation}")

            if result.supporting_evidence:
                print("\nTop Regulatory Evidence Excerpts:")
                for idx, ev in enumerate(result.supporting_evidence, 1):
                    print(f"  [{idx}] {ev}")
            print("-" * 70)

        except (KeyboardInterrupt, EOFError):
            print("\nSession interrupted. Exiting.")
            sys.exit(0)


if __name__ == "__main__":
    run_cli()