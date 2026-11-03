from django.db import models

BLANK_MARKER = "____"


class Level(models.Model):
    number = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=100)
    topic = models.CharField(max_length=100, help_text="Short topic label, e.g. 'print()'")
    summary = models.CharField(max_length=255)
    lesson_markdown = models.TextField(help_text="Lesson explanation (Markdown).")

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return f"Level {self.number}: {self.title}"


class Exercise(models.Model):
    """Exactly ONE exercise per level: a code block with missing lines.

    In ``template_code`` every line whose content is ``____`` is a missing line the
    student must type. Indentation in front of ``____`` is kept, so the student
    only types the code itself.
    """

    level = models.OneToOneField(Level, on_delete=models.CASCADE, related_name="exercise")
    instructions_markdown = models.TextField()
    template_code = models.TextField()
    solution_lines = models.JSONField(help_text="One correct answer per missing line (in order).")
    stdin_cases = models.JSONField(
        default=list,
        help_text="List of test inputs. Each item is a string, one input() value per line.",
    )
    constraints = models.JSONField(
        default=dict,
        blank=True,
        help_text='e.g. {"must_call": ["print"], "must_use": ["for"], "must_assign": ["age"]}',
    )
    static_hints = models.JSONField(help_text="3 escalating hints used when the AI is unavailable.")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Exercise for {self.level}"

    # ---- helpers --------------------------------------------------------
    @property
    def template_lines(self):
        return self.template_code.splitlines()

    @property
    def blank_line_numbers(self):
        """1-based line numbers of the missing lines."""
        return [i + 1 for i, line in enumerate(self.template_lines) if line.strip() == BLANK_MARKER]

    @property
    def blank_count(self):
        return len(self.blank_line_numbers)

    def assemble(self, answers):
        """Insert the student's answers into the template and return full code."""
        answers = list(answers)
        out, k = [], 0
        for line in self.template_lines:
            if line.strip() == BLANK_MARKER:
                indent = line[: len(line) - len(line.lstrip())]
                answer = answers[k] if k < len(answers) else ""
                out.append(indent + str(answer).strip())
                k += 1
            else:
                out.append(line)
        return "\n".join(out) + "\n"

    def reference_code(self):
        return self.assemble(self.solution_lines)

    def editor_rows(self):
        """Rows for the template: [{'n', 'blank', 'indent', 'text', 'blank_index'}]."""
        rows, k = [], 0
        for i, line in enumerate(self.template_lines):
            is_blank = line.strip() == BLANK_MARKER
            rows.append(
                {
                    "n": i + 1,
                    "blank": is_blank,
                    "indent": line[: len(line) - len(line.lstrip())] if is_blank else "",
                    "text": "" if is_blank else line,
                    "blank_index": k if is_blank else None,
                }
            )
            if is_blank:
                k += 1
        return rows
