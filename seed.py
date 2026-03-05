# seed.py

"""
Script para popular o banco de dados com dados iniciais.

Uso:
    python seed.py

O que faz:
    - Cria usuário admin padrão
    - Cria categorias básicas
    - Cria produtos de exemplo
"""

from decimal import Decimal
from sqlmodel import Session, select
from app.database import engine, create_db_and_tables
from app.models import User, Category, Product
from app.auth import get_password_hash


def clear_database(session: Session):
    """
    Limpa todas as tabelas (cuidado em produção!).
    Usado apenas para desenvolvimento/testes.
    """
    print("🗑️  Limpando banco de dados...")
    
    # Deleta na ordem correta (relacionamentos)
    session.query(Product).delete()
    session.query(Category).delete()
    session.query(User).delete()
    
    session.commit()
    print("✅ Banco de dados limpo!")


def create_admin_user(session: Session):
    """
    Cria usuário admin padrão se não existir.
    """
    print("\n👤 Criando usuário admin...")
    
    # Verifica se já existe
    statement = select(User).where(User.username == "admin")
    existing_user = session.exec(statement).first()
    
    if existing_user:
        print("⚠️  Usuário 'admin' já existe. Pulando...")
        return existing_user
    
    # Cria admin
    admin = User(
        username="admin",
        email="admin@geekstore.com",
        hashed_password=get_password_hash("admin123"),
        is_active=True
    )
    
    session.add(admin)
    session.commit()
    session.refresh(admin)
    
    print(f"✅ Admin criado!")
    print(f"   Username: admin")
    print(f"   Password: admin123")
    print(f"   Email: admin@geekstore.com")
    
    return admin


def create_categories(session: Session):
    """
    Cria categorias básicas.
    """
    print("\n📁 Criando categorias...")
    
    categories_data = [
        {
            "name": "Animes",
            "description": "Produtos relacionados a animes japoneses: figures, camisetas, posters e muito mais",
            "slug": "animes"
        },
        {
            "name": "Games",
            "description": "Jogos de videogame, consoles e acessórios para todas as plataformas",
            "slug": "games"
        },
        {
            "name": "Mangás",
            "description": "Mangás e light novels em português e japonês",
            "slug": "mangas"
        },
        {
            "name": "Action Figures",
            "description": "Bonecos colecionáveis de alta qualidade de diversas franquias",
            "slug": "action-figures"
        },
        {
            "name": "Acessórios",
            "description": "Chaveiros, canecas, almofadas, mochilas e outros acessórios geek",
            "slug": "acessorios"
        },
        {
            "name": "Camisetas",
            "description": "Camisetas temáticas de animes, games e cultura pop",
            "slug": "camisetas"
        }
    ]
    
    created_categories = []
    
    for cat_data in categories_data:
        # Verifica se já existe
        statement = select(Category).where(Category.slug == cat_data["slug"])
        existing = session.exec(statement).first()
        
        if existing:
            print(f"⚠️  Categoria '{cat_data['name']}' já existe. Pulando...")
            created_categories.append(existing)
            continue
        
        category = Category(**cat_data)
        session.add(category)
        created_categories.append(category)
        print(f"✅ Categoria '{cat_data['name']}' criada!")
    
    session.commit()
    
    # Refresh para pegar IDs
    for cat in created_categories:
        session.refresh(cat)
    
    return created_categories


def create_products(session: Session, categories: list[Category]):
    """
    Cria produtos de exemplo.
    """
    print("\n📦 Criando produtos...")
    
    # Mapeia categorias por nome para facilitar
    cat_map = {cat.name: cat for cat in categories}
    
    products_data = [
        # ANIMES
        {
            "nome": "Action Figure Naruto Uzumaki",
            "descricao": "Action figure articulada do protagonista Naruto Uzumaki em sua forma Hokage. Inclui acessórios: Kunai, Rasengan effect e capa de Hokage removível. Altura: 18cm.",
            "preco": Decimal("299.90"),
            "quantidade_estoque": 45,
            "image_url": "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=500",
            "category_id": cat_map["Animes"].id,
            "franquia": "Naruto Shippuden"
        },
        {
            "nome": "Nendoroid Luffy Gear 5",
            "descricao": "Nendoroid oficial do Monkey D. Luffy em sua forma Gear 5. Super articulado com expressões intercambiáveis e efeitos especiais. Edição limitada!",
            "preco": Decimal("349.90"),
            "quantidade_estoque": 23,
            "image_url": "https://images.unsplash.com/photo-1613376023733-0a73315d9b06?w=500",
            "category_id": cat_map["Animes"].id,
            "franquia": "One Piece"
        },
        {
            "nome": "Poster Demon Slayer",
            "descricao": "Poster oficial de Demon Slayer (Kimetsu no Yaiba) com os personagens principais. Tamanho: 60x90cm. Papel fotográfico de alta qualidade.",
            "preco": Decimal("39.90"),
            "quantidade_estoque": 120,
            "image_url": "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=500",
            "category_id": cat_map["Animes"].id,
            "franquia": "Demon Slayer"
        },
        
        # GAMES
        {
            "nome": "Controle DualSense PS5",
            "descricao": "Controle sem fio oficial para PlayStation 5 com feedback háptico e gatilhos adaptáveis. Cor: Branco/Preto.",
            "preco": Decimal("449.90"),
            "quantidade_estoque": 67,
            "image_url": "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=500",
            "category_id": cat_map["Games"].id,
            "franquia": "PlayStation"
        },
        {
            "nome": "The Legend of Zelda: Tears of the Kingdom",
            "descricao": "Jogo físico lacrado para Nintendo Switch. Continue a aventura épica de Link em Hyrule!",
            "preco": Decimal("299.00"),
            "quantidade_estoque": 34,
            "image_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=500",
            "category_id": cat_map["Games"].id,
            "franquia": "The Legend of Zelda"
        },
        {
            "nome": "Headset Gamer RGB",
            "descricao": "Headset gamer com som surround 7.1, microfone removível e iluminação RGB personalizável. Compatível com PC, PS5, Xbox e Switch.",
            "preco": Decimal("279.90"),
            "quantidade_estoque": 56,
            "image_url": "https://images.unsplash.com/photo-1599669454699-248893623440?w=500",
            "category_id": cat_map["Games"].id,
            "franquia": "Acessórios Gaming"
        },
        
        # MANGÁS
        {
            "nome": "Mangá One Piece Vol. 1",
            "descricao": "Primeiro volume do mangá One Piece de Eiichiro Oda. Edição brasileira da Panini. Estado: novo e lacrado.",
            "preco": Decimal("18.90"),
            "quantidade_estoque": 89,
            "image_url": "https://images.unsplash.com/photo-1618519764620-7403abdbdfe9?w=500",
            "category_id": cat_map["Mangás"].id,
            "franquia": "One Piece"
        },
        {
            "nome": "Box Chainsaw Man Volumes 1-5",
            "descricao": "Box especial com os 5 primeiros volumes de Chainsaw Man. Inclui pôster exclusivo e marcador de página.",
            "preco": Decimal("149.90"),
            "quantidade_estoque": 28,
            "image_url": "https://images.unsplash.com/photo-1621351183012-e2f9972dd9bf?w=500",
            "category_id": cat_map["Mangás"].id,
            "franquia": "Chainsaw Man"
        },
        {
            "nome": "Jujutsu Kaisen Vol. 0",
            "descricao": "Volume 0 (prelúdio) do mangá Jujutsu Kaisen, base do filme. Edição especial com capa alternativa.",
            "preco": Decimal("24.90"),
            "quantidade_estoque": 71,
            "image_url": "https://images.unsplash.com/photo-1612178537253-bccd437b730e?w=500",
            "category_id": cat_map["Mangás"].id,
            "franquia": "Jujutsu Kaisen"
        },
        
        # ACTION FIGURES
        {
            "nome": "S.H.Figuarts Goku Ultra Instinct",
            "descricao": "Action figure premium da Bandai. Goku na forma Ultra Instinto Dominado com efeitos de aura e múltiplas mãos intercambiáveis. 14cm.",
            "preco": Decimal("459.90"),
            "quantidade_estoque": 15,
            "image_url": "https://images.unsplash.com/photo-1601814933824-fd0b574dd592?w=500",
            "category_id": cat_map["Action Figures"].id,
            "franquia": "Dragon Ball Super"
        },
        {
            "nome": "Funko Pop Spider-Man Miles Morales",
            "descricao": "Funko Pop do Miles Morales (Spider-Verse). Edição exclusiva com efeito de teia brilha no escuro. 10cm.",
            "preco": Decimal("129.90"),
            "quantidade_estoque": 92,
            "image_url": "https://images.unsplash.com/photo-1608889476561-6242cfdbf622?w=500",
            "category_id": cat_map["Action Figures"].id,
            "franquia": "Spider-Man"
        },
        
        # ACESSÓRIOS
        {
            "nome": "Caneca Geek 'Code Master'",
            "descricao": "Caneca de porcelana 350ml com estampa 'Code Master' em ASCII art. Perfeita para desenvolvedores! Microondas e lava-louças safe.",
            "preco": Decimal("39.90"),
            "quantidade_estoque": 156,
            "image_url": "https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=500",
            "category_id": cat_map["Acessórios"].id,
            "franquia": "Tech Geek"
        },
        {
            "nome": "Chaveiro Pokébola",
            "descricao": "Chaveiro metálico em formato de Pokébola com LEDs internos. Abre e fecha! Funciona com bateria (inclusa).",
            "preco": Decimal("34.90"),
            "quantidade_estoque": 203,
            "image_url": "https://images.unsplash.com/photo-1542779283-429940ce8336?w=500",
            "category_id": cat_map["Acessórios"].id,
            "franquia": "Pokémon"
        },
        {
            "nome": "Mochila Tactical Geek",
            "descricao": "Mochila estilo militar/tático com compartimento para notebook 15.6', USB charging port e múltiplos bolsos. Resistente à água.",
            "preco": Decimal("189.90"),
            "quantidade_estoque": 43,
            "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500",
            "category_id": cat_map["Acessórios"].id,
            "franquia": "Tech Gear"
        },
        
        # CAMISETAS
        {
            "nome": "Camiseta Akatsuki",
            "descricao": "Camiseta preta 100% algodão com logo da Akatsuki (Naruto). Tamanhos: P, M, G, GG. Estampa de alta qualidade.",
            "preco": Decimal("79.90"),
            "quantidade_estoque": 87,
            "image_url": "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=500",
            "category_id": cat_map["Camisetas"].id,
            "franquia": "Naruto"
        },
        {
            "nome": "Camiseta Retro Gaming 8-bit",
            "descricao": "Camiseta com design retrô de videogames clássicos em pixel art. 100% algodão, corte unissex.",
            "preco": Decimal("69.90"),
            "quantidade_estoque": 124,
            "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=500",
            "category_id": cat_map["Camisetas"].id,
            "franquia": "Retro Games"
        },
    ]
    
    created_products = []
    
    for prod_data in products_data:
        # Verifica se já existe (por nome)
        statement = select(Product).where(Product.nome == prod_data["nome"])
        existing = session.exec(statement).first()
        
        if existing:
            print(f"⚠️  Produto '{prod_data['nome']}' já existe. Pulando...")
            created_products.append(existing)
            continue
        
        product = Product(**prod_data)
        session.add(product)
        created_products.append(product)
        print(f"✅ Produto '{prod_data['nome']}' criado! (R$ {prod_data['preco']})")
    
    session.commit()
    print(f"\n🎉 {len(created_products)} produtos criados com sucesso!")
    
    return created_products


def print_summary(session: Session):
    """
    Imprime resumo do banco de dados.
    """
    print("\n" + "="*60)
    print("📊 RESUMO DO BANCO DE DADOS")
    print("="*60)
    
    # Usuários
    users_count = session.exec(select(User)).all()
    print(f"\n👥 Usuários: {len(users_count)}")
    for user in users_count:
        print(f"   - {user.username} ({user.email})")
    
    # Categorias
    categories = session.exec(select(Category)).all()
    print(f"\n📁 Categorias: {len(categories)}")
    for cat in categories:
        products_count = len(cat.products)
        print(f"   - {cat.name}: {products_count} produtos")
    
    # Produtos
    products = session.exec(select(Product)).all()
    total_value = sum(p.preco * p.quantidade_estoque for p in products)
    print(f"\n📦 Produtos: {len(products)}")
    print(f"💰 Valor total do estoque: R$ {total_value:,.2f}")
    
    print("\n" + "="*60)
    print("✅ SEED CONCLUÍDO COM SUCESSO!")
    print("="*60)
    print("\n🚀 Acesse a API:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - Documentação: http://localhost:8000/redoc")
    print("\n🔐 Credenciais de login:")
    print("   - Username: admin")
    print("   - Password: admin123")
    print("="*60 + "\n")


def main():
    """
    Função principal do seed.
    """
    print("\n" + "="*60)
    print("🌱 SEED DO BANCO DE DADOS - GEEK STORE")
    print("="*60)
    
    # Cria tabelas se não existirem
    print("\n📋 Verificando tabelas...")
    create_db_and_tables()
    print("✅ Tabelas verificadas!")
    
    with Session(engine) as session:
        # Pergunta se quer limpar o banco
        print("\n⚠️  ATENÇÃO: Deseja limpar o banco de dados antes de popular?")
        print("   Isso irá DELETAR todos os dados existentes!")
        choice = input("   Digite 'SIM' para confirmar ou Enter para pular: ").strip().upper()
        
        if choice == "SIM":
            clear_database(session)
        else:
            print("⏭️  Pulando limpeza do banco...")
        
        # Cria dados
        admin = create_admin_user(session)
        categories = create_categories(session)
        products = create_products(session, categories)
        
        # Resumo
        print_summary(session)


if __name__ == "__main__":
    main()