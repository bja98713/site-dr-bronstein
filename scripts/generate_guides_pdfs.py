from __future__ import annotations

from pathlib import Path

from fpdf import FPDF


def _write_pdf(out_path: Path, title: str, summary: str, steps: list[str]) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_page()

    # Core fonts (Helvetica) support latin-1/cp1252; OK for French accents.
    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 9, title)

    pdf.ln(2)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(60, 60, 60)
    pdf.multi_cell(0, 7, summary)

    pdf.ln(4)
    pdf.set_text_color(15, 23, 42)
    for idx, step in enumerate(steps, start=1):
        pdf.multi_cell(0, 7, f"{idx}. {step}")
        pdf.ln(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "static" / "docs"

    guides = [
        {
            "filename": "preparation-coloscopie.pdf",
            "title": "Comment se préparer à une coloscopie",
            "summary": "Étapes la veille et le jour J, diète et laxatif.",
            "steps": [
                "Régime pauvre en résidus la veille (précisions sur l'ordonnance).",
                "Boire le laxatif aux horaires indiqués, en fractionnant si besoin.",
                "Hydratation par liquides clairs jusqu'à l'horaire autorisé.",
                "Arriver accompagné si anesthésie; ne pas conduire après l'examen.",
            ],
        },
        {
            "filename": "deroulement-fibroscopie.pdf",
            "title": "Comment se déroule une fibroscopie",
            "summary": "Durée de l'examen, anesthésie et reprise alimentaire.",
            "steps": [
                "Jeûne de 6h pour solides et 2h pour liquides clairs, sauf consigne différente.",
                "Sédation courte ou anesthésie selon indication; durée d'examen environ 10 minutes.",
                "Surveillance en salle de réveil; reprise alimentaire légère après accord médical.",
                "Ne pas conduire le jour même en cas de sédation/anesthésie.",
            ],
        },
        {
            "filename": "anesthesie-endoscopie.pdf",
            "title": "Anesthésie pour endoscopie : questions fréquentes",
            "summary": "Sécurité, jeûne, reprise des traitements habituels.",
            "steps": [
                "Respecter le jeûne indiqué; signaler tout traitement (anticoagulant, antiagrégant).",
                "Prendre les traitements autorisés avec une petite gorgée d'eau si prescrit.",
                "Prévoir un accompagnant; ne pas conduire ni signer de documents importants le jour même.",
                "En cas de fièvre ou symptômes la veille, prévenir le secrétariat/anesthésiste.",
            ],
        },
        {
            "filename": "recommandations-post-examen.pdf",
            "title": "Recommandations après l'examen",
            "summary": "Surveillance à domicile, reprise alimentaire, signes d'alerte.",
            "steps": [
                "Repos le jour même en cas d'anesthésie; ne pas conduire.",
                "Reprise alimentaire progressive selon consignes du médecin.",
                "Surveiller l'apparition de douleurs importantes, fièvre, vomissements ou saignements.",
                "Contacter le cabinet ou les urgences en cas de signe d'alerte.",
            ],
        },
    ]

    for guide in guides:
        _write_pdf(
            out_path=out_dir / guide["filename"],
            title=guide["title"],
            summary=guide["summary"],
            steps=guide["steps"],
        )

    print("Generated PDFs in", out_dir)


if __name__ == "__main__":
    main()
