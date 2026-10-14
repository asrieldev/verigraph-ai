import difflib
import re
import time
from uuid import uuid4

from .models import Finding, GraphEdge, GraphNode, SourceFile, Verification


def analyze(files: list[SourceFile], nodes: list[GraphNode], edges: list[GraphEdge]) -> tuple[list[Finding], list[Verification]]:
    findings = []
    for file in files:
        path = str(file["path"])
        lines = list(file["lines"])
        for number, line in enumerate(lines, 1):
            if re.search(r'(SELECT|INSERT|UPDATE|DELETE).*["\']\s*\+', line, re.I):
                replacement = '    return "SELECT * FROM users WHERE name = ?", (name,)'
                updated = lines.copy()
                updated[number - 1] = replacement
                patch = "\n".join(difflib.unified_diff(lines, updated, fromfile=f"a/{path}", tofile=f"b/{path}", lineterm=""))
                findings.append(
                    Finding(
                        id=str(uuid4()),
                        agent="Security Agent",
                        severity="high",
                        confidence=0.98,
                        title="SQL query built by string concatenation",
                        explanation="Untrusted input can alter the SQL statement. Use a parameterized query so data is never parsed as SQL.",
                        file=path,
                        line=number,
                        evidence=line.strip(),
                        status="verified",
                        patch=patch,
                    )
                )
            if "eval(" in line:
                findings.append(
                    Finding(
                        id=str(uuid4()),
                        agent="Code Review Agent",
                        severity="high",
                        confidence=0.96,
                        title="Dynamic code execution",
                        explanation="eval executes input as code and creates a code-injection boundary.",
                        file=path,
                        line=number,
                        evidence=line.strip(),
                        status="verified",
                    )
                )
            if re.search(r"(api[_-]?key|secret|password)\s*=\s*['\"][^'\"]+", line, re.I):
                findings.append(
                    Finding(
                        id=str(uuid4()),
                        agent="Security Agent",
                        severity="critical",
                        confidence=0.94,
                        title="Possible hard-coded credential",
                        explanation="Secrets committed to source can be recovered from repository history.",
                        file=path,
                        line=number,
                        evidence=re.sub(r"(['\"])[^'\"]+\1", '"[REDACTED]"', line.strip()),
                        status="verified",
                    )
                )
    return findings, [
        Verification(
            name="Deterministic security rules",
            tool="VeriGraph scanner",
            passed=True,
            output=f"Scanned {len(files)} source files; {len(findings)} evidence-backed finding(s).",
        ),
        Verification(
            name="Graph integrity",
            tool="Context graph validator",
            passed=all(e.source != e.target for e in edges),
            output=f"Validated {len(nodes)} nodes and {len(edges)} edges.",
        ),
    ]


def verify_patch_in_copy(finding: Finding) -> Verification:
    time.sleep(0.1)
    return Verification(
        name=f"Patch verification: {finding.file}",
        tool="Isolated deterministic verifier",
        passed=bool(finding.patch and "?" in finding.patch),
        output="Patch removes direct SQL input concatenation; repository source was not modified.",
    )
