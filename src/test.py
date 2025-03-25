import os
import subprocess
import tempfile


def format_java_method(method_code: str) -> str:
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".java", delete=False) as tmp:
        tmp.write(method_code)
        tmp_path = tmp.name

    # Format with Prettier
    result = subprocess.run(
        ["npx", "prettier", "--plugin=prettier-plugin-java", "--write", tmp_path],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        os.unlink(tmp_path)  # Delete temp file on error
        raise Exception(f"Prettier failed: {result.stderr}")

    # Read back the formatted method
    with open(tmp_path, "r") as f:
        formatted_code = f.read().strip()

    os.unlink(tmp_path)  # Delete temp file before returning
    return formatted_code


# Test
java_method = """public int add(int a, int b) {return a + b;}"""
print(format_java_method(java_method))
