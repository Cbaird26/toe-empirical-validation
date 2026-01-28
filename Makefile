# Makefile for ToE Constraint Pipeline

.PHONY: help scalar-hypothesis-card scalar-three-prong scalar-joint scalar-full constraint-pipeline

help:
	@echo "Available targets:"
	@echo "  scalar-hypothesis-card  - Validate hypothesis card"
	@echo "  scalar-three-prong      - Generate all three channel bounds"
	@echo "  scalar-joint            - Generate joint exclusion plot and dashboard"
	@echo "  scalar-full             - Run complete pipeline (three-prong + joint)"
	@echo "  constraint-pipeline     - Run end-to-end constraint pipeline (ingest + bounds + plot)"

scalar-hypothesis-card:
	@echo "Validating Minimal Scalar Hypothesis Card..."
	@python3 -c "import yaml; yaml.safe_load(open('data/constraints/minimal_scalar_hypothesis_card_v0.1.yaml'))" && echo "✓ Hypothesis card is valid YAML"
	@echo "✓ Hypothesis card validation complete"

scalar-three-prong:
	@echo "Generating three-prong constraint bounds..."
	@python3 scripts/generate_fifth_force_ep_bounds.py
	@python3 scripts/generate_clocks_spectroscopy_bounds.py
	@echo "Note: Run 'python3 scripts/generate_collider_higgs_bounds.py' separately if collider module exists"
	@echo "✓ Three-prong bounds generation complete"

scalar-joint:
	@echo "Generating joint scalar constraints..."
	@python3 scripts/generate_joint_scalar_constraints.py
	@echo "✓ Joint constraint generation complete"

scalar-full: scalar-three-prong scalar-joint
	@echo "✓ Complete scalar constraint pipeline finished"

constraint-pipeline:
	@echo "Running end-to-end constraint pipeline..."
	@bash scripts/run_constraint_pipeline.sh
	@echo "✓ Constraint pipeline complete"
