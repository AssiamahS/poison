SKILL_DIR := $(HOME)/.claude/skills/poison
SRC       := skill

.PHONY: install uninstall check info dry-run

install: 
	mkdir -p $(HOME)/.local/bin && cp bin/poison $(HOME)/.local/bin/poison && chmod +x $(HOME)/.local/bin/poison
	mkdir -p $(SKILL_DIR)
	rsync -a --delete --exclude node_modules --exclude 'public/job' $(SRC)/ $(SKILL_DIR)/
	@if [ -d $(SRC)/video/node_modules ]; then ln -sfn $(CURDIR)/$(SRC)/video/node_modules $(SKILL_DIR)/video/node_modules; fi
	chmod +x $(SKILL_DIR)/scripts/poison_gen.py $(SKILL_DIR)/scripts/poison_video.py
	@echo "installed to $(SKILL_DIR) — type /poison in Claude Code"

uninstall:
	rm -rf $(SKILL_DIR)
	@echo "removed $(SKILL_DIR)"

check:
	@command -v python3 >/dev/null || (echo "python3 missing" && exit 1)
	@test -f $(SRC)/SKILL.md || (echo "$(SRC)/SKILL.md missing" && exit 1)
	@test -f $(SRC)/scripts/poison_gen.py || (echo "generator missing" && exit 1)
	@ls $(SRC)/styles/*.md >/dev/null
	@python3 $(SRC)/scripts/poison_gen.py --dry-run

info:
	@echo "poison — visual explanations from any topic"
	@echo "styles: $$(ls $(SRC)/styles | sed 's/\.md//' | tr '\n' ' ')"
	@echo "installed: $$(test -f $(SKILL_DIR)/SKILL.md && echo yes || echo no)"

dry-run: check
