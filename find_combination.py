import itertools

valores = [
    ('Eixo Bluetec 1', 14930.18),
    ('Eixo Sebratec', 14930.18),
    ('Eixo Bluetec 2', 14930.18),
    ('JC 120', 2994.77),
    ('Apresentação 1', 0.00),
    ('GA000-003', 5747.80),
    ('Apresentação 2', 0.00),
    ('Acoplamento', 11193.00),
]

target = 55983.54

print(f"Buscando combinação que soma R$ {target:,.2f}...\n")

for r in range(1, len(valores)+1):
    for combo in itertools.combinations(valores, r):
        total = sum(v for n, v in combo)
        if abs(total - target) < 1:
            print(f"✅ ENCONTRADO! {len(combo)} negócios:")
            for nome, valor in combo:
                print(f"   - {nome}: R$ {valor:,.2f}")
            print(f"\n📊 Total: R$ {total:,.2f}")
            print(f"📊 Ticket médio: R$ {total/len(combo):,.2f}")
            break
