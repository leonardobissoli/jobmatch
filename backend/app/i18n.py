"""ADR-013 — backend i18n.

PT-BR is the source of truth (legal copy, default). EN values are free
translations locked to a glossary of proper nouns (`Tech Hub`, `Job Match`,
`Leonardo Bissoli`, `LinkedIn`).

`resolve_locale()` reads `Accept-Language` and falls back to `pt-BR`.
Frontend also sends a `locale` form field on `/api/v1/match` which takes
precedence (explicit user choice from the LocaleSwitcher).
"""
from __future__ import annotations

DEFAULT_LOCALE = "pt-BR"
SUPPORTED_LOCALES = ("pt-BR", "en")


_MESSAGES: dict[str, dict[str, str]] = {
    "pt-BR": {
        # === Form-level errors (routes/match.py) ===
        "errors.cv_job_conflict": "Envie a vaga como arquivo OU texto colado, não ambos.",
        "errors.missing_job": "Envie a descrição da vaga (arquivo ou texto colado).",
        "errors.payload_too_large_combined": "Arquivo excede o limite permitido (CV até 5MB, vaga até 100KB).",
        "errors.invalid_cv_type": "Tipo de arquivo inválido. Envie o CV em PDF.",
        "errors.invalid_job_type": "Tipo de arquivo inválido. Envie a vaga em TXT.",
        "errors.cv_too_large": "CV excede o limite de 5MB.",
        "errors.job_too_large": "Descrição da vaga excede o limite de 100KB.",
        "errors.empty_files": "Arquivos vazios.",
        "errors.llm_unavailable": "Estamos com dificuldade pra processar agora. Tente novamente em alguns minutos.",
        "errors.internal": "Erro interno. Tente novamente.",
        # === Local LLM mode (ADR-026) ===
        "errors.local_llm_invalid": "Configuração do modelo local inválida. O endereço precisa apontar pra sua própria máquina (localhost ou 127.0.0.1).",
        "errors.local_llm_unreachable": "Não conseguimos falar com o servidor local. Verifique se o Ollama ou o LM Studio está rodando no endereço informado.",
        "errors.local_llm_bad_output": "O modelo local devolveu um resultado fora do formato esperado. Modelos pequenos costumam falhar nisso — tente um modelo maior.",
        "errors.local_llm_insufficient_data": "O modelo local não conseguiu analisar os arquivos. Modelos pequenos costumam falhar nisso — tente um modelo maior.",
        # === Content validation (job_match_engine.py) ===
        "errors.content.insufficient_data": "Os arquivos não têm dados suficientes para gerar uma análise. Verifique se o CV inclui experiências e a vaga inclui requisitos.",
        "errors.content.cv_validation_failed": "O arquivo enviado não foi reconhecido como um currículo válido. Confira o arquivo e tente novamente.",
        "errors.content.job_validation_failed": "O texto enviado não foi reconhecido como uma descrição de vaga. Confira o conteúdo e tente novamente.",
        "errors.content.suspicious_content_cv": "Não conseguimos processar esse arquivo.",
        "errors.content.suspicious_content_job": "Não conseguimos processar esse arquivo.",
        "errors.content.fallback": "Não conseguimos processar esse arquivo.",
        # === Resume length (services/job_match_engine.py) ===
        "resume_length.short": "CV muito curto. Você pode estar subaproveitando suas experiências — inclua mais detalhes em conquistas, responsabilidades e resultados mensuráveis.",
        "resume_length.long": "CV longo. Recrutadores escaneiam em poucos segundos — corte experiências antigas ou irrelevantes para a vaga e foque no que importa.",
        "resume_length.ideal": "Tamanho ideal. Bom equilíbrio entre detalhe e legibilidade.",
        # === PDF parse user messages (routes/match.py) ===
        "pdf.password_protected": "O CV está protegido por senha. Salve uma versão sem senha e tente novamente.",
        "pdf.dangerous_feature": "Não conseguimos processar esse PDF. Use um arquivo padrão, sem recursos especiais ou anexos.",
        "pdf.invalid_magic": "O arquivo do CV não é um PDF válido. Verifique o formato e tente novamente.",
        "pdf.no_text": "Não conseguimos extrair texto do seu CV. Envie um PDF de texto (não escaneado/imagem).",
        "pdf.timeout": "O CV demorou demais pra processar. Tente um arquivo mais simples.",
        "pdf.too_large": "O CV é muito grande pra processar. Envie um arquivo menor.",
        "pdf.corrupt": "O CV parece corrompido. Salve novamente como PDF e tente.",
        "pdf.fallback": "Não conseguimos ler o CV. Envie um PDF de texto válido.",
        # === TXT parse user messages (routes/match.py) ===
        "txt.empty": "A descrição da vaga está vazia.",
        "txt.binary": "A descrição da vaga precisa ser um arquivo de texto (.txt). Cole o conteúdo da vaga em texto puro e salve como .txt.",
        "txt.decode": "Não conseguimos ler a descrição da vaga. Salve o arquivo como UTF-8 e tente novamente.",
        "txt.too_short": "A descrição da vaga é muito curta. Inclua pelo menos os requisitos e responsabilidades.",
        "txt.fallback": "Descrição da vaga inválida.",
    },
    "en": {
        "errors.cv_job_conflict": "Send the job as either a file or pasted text, not both.",
        "errors.missing_job": "Send the job description (file or pasted text).",
        "errors.payload_too_large_combined": "File exceeds the allowed limit (CV up to 5MB, job up to 100KB).",
        "errors.invalid_cv_type": "Invalid file type. Send the CV as a PDF.",
        "errors.invalid_job_type": "Invalid file type. Send the job as a TXT file.",
        "errors.cv_too_large": "CV exceeds the 5MB limit.",
        "errors.job_too_large": "Job description exceeds the 100KB limit.",
        "errors.empty_files": "Empty files.",
        "errors.llm_unavailable": "We're having trouble processing right now. Please try again in a few minutes.",
        "errors.internal": "Internal error. Please try again.",
        # === Local LLM mode (ADR-026) ===
        "errors.local_llm_invalid": "Invalid local model configuration. The address must point to your own machine (localhost or 127.0.0.1).",
        "errors.local_llm_unreachable": "Could not reach the local server. Check that Ollama or LM Studio is running at the address you entered.",
        "errors.local_llm_bad_output": "The local model returned a result outside the expected format. Small models often fail at this — try a larger one.",
        "errors.local_llm_insufficient_data": "The local model couldn't analyze the files. Small models often fail at this — try a larger one.",
        "errors.content.insufficient_data": "The files don't have enough data to generate an analysis. Make sure the CV includes experience and the job includes requirements.",
        "errors.content.cv_validation_failed": "The file you sent wasn't recognized as a valid resume. Check the file and try again.",
        "errors.content.job_validation_failed": "The text you sent wasn't recognized as a job description. Check the content and try again.",
        "errors.content.suspicious_content_cv": "We couldn't process that file.",
        "errors.content.suspicious_content_job": "We couldn't process that file.",
        "errors.content.fallback": "We couldn't process that file.",
        "resume_length.short": "CV is too short. You may be underusing your experience — add more detail on achievements, responsibilities, and measurable results.",
        "resume_length.long": "CV is long. Recruiters scan in seconds — cut older or irrelevant experience and focus on what matters.",
        "resume_length.ideal": "Ideal length. Good balance between detail and readability.",
        "pdf.password_protected": "Your CV is password-protected. Save an unprotected version and try again.",
        "pdf.dangerous_feature": "We couldn't process that PDF. Use a standard file without special features or attachments.",
        "pdf.invalid_magic": "Your CV file isn't a valid PDF. Check the format and try again.",
        "pdf.no_text": "We couldn't extract text from your CV. Send a text-based PDF (not scanned/image).",
        "pdf.timeout": "Your CV took too long to process. Try a simpler file.",
        "pdf.too_large": "Your CV is too large to process. Send a smaller file.",
        "pdf.corrupt": "Your CV appears to be corrupted. Save it again as a PDF and try again.",
        "pdf.fallback": "We couldn't read your CV. Send a valid text-based PDF.",
        "txt.empty": "The job description is empty.",
        "txt.binary": "The job description needs to be a text file (.txt). Paste the job content in plain text and save as .txt.",
        "txt.decode": "We couldn't read the job description. Save the file as UTF-8 and try again.",
        "txt.too_short": "The job description is too short. Include at least the requirements and responsibilities.",
        "txt.fallback": "Invalid job description.",
    },
}


def t(locale: str, key: str, **kwargs) -> str:
    """Look up a localized string. Falls back to pt-BR if key missing in target locale."""
    bucket = _MESSAGES.get(locale) or _MESSAGES[DEFAULT_LOCALE]
    template = bucket.get(key) or _MESSAGES[DEFAULT_LOCALE].get(key) or key
    if kwargs:
        try:
            return template.format(**kwargs)
        except (KeyError, IndexError):
            return template
    return template


def resolve_locale(accept_language: str | None, form_locale: str | None = None) -> str:
    """Pick a supported locale from explicit form field → Accept-Language → default.

    Frontend sends `locale` form field on POST /api/v1/match. Trust that first.
    """
    if form_locale and form_locale in SUPPORTED_LOCALES:
        return form_locale
    if accept_language:
        for raw in accept_language.split(","):
            primary = raw.split(";")[0].strip().lower()
            if primary.startswith("en"):
                return "en"
            if primary.startswith("pt"):
                return "pt-BR"
    return DEFAULT_LOCALE
