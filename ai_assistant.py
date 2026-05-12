import os

from dotenv import load_dotenv
from openai import OpenAI


class AIChatAssistant:
    def __init__(self, inventory_service):
        self.inventory_service = inventory_service
        load_dotenv()

    def generate_response(self, question, role):
        context = self.inventory_service.get_ai_context()
        api_key = self.get_api_key()
        model = self.get_model()

        if not api_key:
            return self.local_answer(question)

        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant for Jacob's Bakery Inventory Manager. Give short, useful answers based only on the bakery data.",
                    },
                    {
                        "role": "user",
                        "content": f"User role: {role}\n\nBakery data:\n{context}\n\nQuestion: {question}",
                    },
                ],
            )
            return response.choices[0].message.content
        except Exception:
            return self.local_answer(question)

    def get_api_key(self):
        return os.getenv("OPENAI_API_KEY")

    def get_model(self):
        return os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def local_answer(self, question):
        question = question.lower()
        summary = self.inventory_service.get_summary()
        low_items = self.inventory_service.get_low_stock_items()

        if "low" in question or "restock" in question:
            if not low_items:
                return "No products are low on stock right now."

            names = []
            for item in low_items:
                names.append(f"{item.name} ({item.stock} left)")
            return "Restock these first: " + ", ".join(names)

        if "sale" in question:
            return f"Total sales recorded so far are ${summary['sales_total']:.2f}."

        if "value" in question or "worth" in question:
            return f"The current inventory value is ${summary['inventory_value']:.2f}."

        return "I can help with low stock, restocking, sales totals, and inventory value."
