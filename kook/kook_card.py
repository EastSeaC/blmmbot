import json

__piece = {
    "type": "kmarkdown",
    "content": "**昵称**\n怪才君"
},


class KookCard:
    def __init__(self):
        self.raw = [
            {
                "type": "card",
                "theme": "secondary",
                "size": "lg",
                "modules": [
                    {
                        "type": "section",
                        "text": {
                            "type": "paragraph",
                            "cols": 3,
                            "fields": [
                            ]
                        }
                    }
                ]
            }
        ]

    def add_pieceEx(self, title: str, content: str):
        piece = {
            "type": "kmarkdown",
            "content": f"**{title}**\n{content}"
        }
        # self.raw[0]["modules"]["text"]
        self.raw[0]["modules"][0]["text"]["fields"].append(piece)

    def add_piece(self, data: dict):
        title = data["title"]
        content = data["content"]

        piece = {
            "type": "kmarkdown",
            "content": f"**{title}**\n{content}"
        }

        self.raw[0]["modules"]["text"]["fields"].append(piece)

    @property
    def get_card_json(self):
        return self.raw


if __name__ == '__main__':
    card = KookCard()
    card.add_pieceEx("baga","ga")
    json_str = json.dumps(card.raw, indent='\t')
    print(json_str)
