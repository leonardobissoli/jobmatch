import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Privacidade local — Job Match",
  robots: { index: false, follow: false },
};

export default function PrivacyPage() {
  return (
    <main className="min-h-screen px-4 py-12 md:py-20">
      <article className="mx-auto max-w-[760px]">
        <Link href="/" className="text-fg-muted hover:text-fg-primary text-sm">
          ← Voltar
        </Link>
        <h1 className="text-3xl md:text-4xl font-bold mt-6 mb-6 text-fg-primary">
          Privacidade na execução local
        </h1>
        <div className="space-y-4 text-fg-muted leading-relaxed">
          <p>
            Esta versão do Job Match roda na sua própria máquina. Ela não solicita e-mail,
            não mantém banco de dados e não armazena CVs, vagas ou relatórios.
          </p>
          <h2 className="text-xl font-bold text-fg-primary mt-8">Provedor selecionado</h2>
          <p>
            Com Ollama ou LM Studio, o processamento ocorre no servidor de modelo instalado
            localmente. Com MiniMax, o texto extraído do CV e da vaga é enviado à API da
            MiniMax usando a chave configurada por você.
          </p>
          <h2 className="text-xl font-bold text-fg-primary mt-8">Arquivos e relatório</h2>
          <p>
            Os arquivos são processados apenas durante a requisição. O PDF do relatório é
            gerado diretamente no navegador e fica sob seu controle.
          </p>
          <h2 className="text-xl font-bold text-fg-primary mt-8">Sua responsabilidade</h2>
          <p>
            Consulte os termos e a política do provedor escolhido antes de enviar dados
            pessoais ou confidenciais.
          </p>
        </div>
      </article>
    </main>
  );
}
