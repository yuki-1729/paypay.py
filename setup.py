from setuptools import setup

with open("requirements.txt", "r", encoding="utf-8", errors="ignore") as file:
    requirements = file.read().splitlines()

with open("README.md", "r", encoding="utf-8", errors="ignore") as file:
    readme = file.read()

setup(
    name="paypay.py",
    author="yuki",
    version="1.0.0",
    packages=["paypay"],
    license="MIT",
    description="PayPay(paypay.ne.jp)用の非公式APIライブラリ",
    long_description=readme,
    requires=requirements,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)