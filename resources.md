# Chain of Ethics: Research Resources

This document catalogs the research, tools, and frameworks that informed the development of the Chain of Ethics alignment benchmark.

## Academic Research

### Ethical Alignment & Evaluation
- [Ethics and Interdiction: Synthetic Ethical Alignment & Evaluating LLM Behaviors](https://arxiv.org/pdf/2312.06315) - Research on methods for measuring and evaluating ethical behavior in language models.
- [Values and Alignment in Language Models](https://arxiv.org/abs/2109.07958) - Comprehensive analysis of approaches to value alignment in modern LLMs.
- [CrowS-Pairs: A Challenge Dataset for Measuring Social Biases in Masked Language Models](https://www.researchgate.net/publication/347235439_CrowS-Pairs_A_Challenge_Dataset_for_Measuring_Social_Biases_in_Masked_Language_Models) - Dataset specifically designed to measure social bias in language models.
- [Refusal in LLMs is Mediated by a Single Direction](https://www.lesswrong.com/posts/jGuXSZgv6qfdhMCuJ/refusal-in-llms-is-mediated-by-a-single-direction) - Analysis of how refusal behaviors are represented in LLM parameter space.

### LLM Evaluation Frameworks
- [Can LLMs Follow Simple Rules?](https://arxiv.org/html/2405.09341v1) - Investigation into LLMs' ability to adhere to explicit behavioral guidelines.
- [A Survey of Safety and Trustworthiness of Large Language Models through the Lens of Verification and Validation](https://arxiv.org/html/2406.04428v1) - Comprehensive review of verification approaches for LLM safety.
- [Automated LLM Evaluation by LLM: Analysis of Capabilities of Self-Evaluations and Peer-Evaluations](https://arxiv.org/abs/2502.01154) - Research on using LLMs to evaluate other LLMs.
- [Towards Reliable Automated Evaluation Metrics for LLM-Generated Content](https://arxiv.org/html/2504.02080v1) - Analysis of automated metrics for evaluating LLM outputs.
- [Comparative Study of Methods for Contextual Bias Mitigation in Language Models](https://aclanthology.org/2021.acl-long.416/) - Research on techniques to reduce contextual biases in LLMs.

### Medical & Healthcare Applications
- [Artificial Intelligence Hallucinations in Medicine: A Cross-sectional Study](https://www.medrxiv.org/content/10.1101/2024.09.18.24313931v2.full.pdf) - Study of hallucination risks in medical AI applications.

## Industry Frameworks & Standards

### Safety & Alignment Frameworks
- [OpenAI Preparedness Framework v2](https://cdn.openai.com/pdf/18a02b5d-6b67-4cec-ab64-68cdfbddebcd/preparedness-framework-v2.pdf) - OpenAI's formal approach to assessing and mitigating potential risks from advanced AI systems.
- [Updating Our Preparedness Framework](https://openai.com/index/updating-our-preparedness-framework/) - OpenAI's evolution of safety frameworks for increasingly capable models.
- [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) - Security risks and mitigations for LLM-based applications.
- [MITRE ATLAS (Adversarial Threat Landscape for Artificial-Intelligence Systems)](https://atlas.mitre.org/) - Knowledge base of adversarial tactics and techniques against AI systems.
- [AISI Inspection Evals](https://inspect.aisi.org.uk/evals/) - Evaluation framework for testing safety properties of language models.
- [GenAIEval Project](https://github.com/opea-project/GenAIEval) - Open-source toolkit for evaluating generative AI models.
- [Turing LLM Alignment and Safety Guide](https://www.turing.com/resources/llm-alignment-and-safety-guide) - Comprehensive guide to alignment concepts and implementation approaches.

### Evaluation Tools & Metrics
- [LLM Evaluation: Ensuring Ethical Standards Alignment](https://www.deepchecks.com/question/llm-evaluation-ensure-ethical-standards-alignment/) - Framework for evaluating LLM adherence to ethical standards.
- [LLM Evaluation: Top 10 Metrics and Benchmarks](https://www.kolena.com/guides/llm-evaluation-top-10-metrics-and-benchmarks/) - Industry guide to evaluation metrics for language models.

## Frontier Models & Capabilities

### Leading Models
- [DeepSeek R1 Model](https://ollama.com/library/deepseek-r1) - Technical specifications and capabilities of the DeepSeek R1 model.
- [Llama 3.3 Model](https://ollama.com/library/llama3.3) - Meta's Llama 3.3 model family information and deployment guides.
- [Google Gemini Models](https://deepmind.google/technologies/gemini/) - Overview of Google's multimodal Gemini model series.
- [GPT-4 Technical Report](https://openai.com/index/gpt-4/) - Technical specifications and capabilities of OpenAI's GPT-4 model family.

### Security Research
- [Novel Universal Bypass for All Major LLMs](https://hiddenlayer.com/innovation-hub/novel-universal-bypass-for-all-major-llms/) - Research on systematic techniques for circumventing safety mechanisms in language models.
- [How to Jailbreak LLMs](https://www.promptfoo.dev/blog/how-to-jailbreak-llms/) - Analysis of methods used to bypass alignment constraints in commercial language models.

## Citations in Repository

Where appropriate, specific techniques, metrics, or approaches from these resources have been cited within our scenario designs, evaluation methodologies, and technical documentation. Key implementations include:

- Ethical axes derived from moral foundations theory (Haidt & Graham)
- Evaluation methodologies inspired by OpenAI's preparedness framework
- Scenario design influenced by values-in-play frameworks (Flanagan & Nissenbaum)
- Scoring mechanisms drawn from multiple ethical evaluation approaches

## Contributing

To add resources to this list:
1. Submit a pull request with your addition
2. Include a brief description of the resource
3. Categorize it appropriately within the existing sections
4. Format consistently with other entries

---

_Last updated: May 2025_