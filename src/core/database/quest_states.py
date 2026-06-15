# src/core/database/quest_states.py
"""
Quest Intelligence (Sprint 13) — estados narrativos nomeados para quest flags.

Hoje QuestFlags[i] é tratado como bool (0/1) pela GUI, mas o array
subjacente já armazena inteiros (`questFlags: list[int]`). Vários flags do
jogo na verdade codificam progressão de várias etapas dentro do mesmo
inteiro — esta tabela documenta, flag a flag, o significado de cada valor
inteiro observável, baseado em engenharia reversa dos scripts de conversa
(.cnv) e em pesquisa da comunidade sobre Ultima Underworld 2.

Formato:
    QUEST_STATES: dict[str, dict[int, dict]] = {
        "<flag_name>": {
            <int_value>: {"label": "<nome curto>", "desc": "<descrição>"},
            ...
        },
        ...
    }

Flags ausentes deste mapeamento são tratados como binários simples
(0 = Inativo / 1+ = Ativo) pela função `describe_state()` abaixo — não é
necessário listar todo QUEST_FLAGS aqui, apenas os que têm progressão
narrativa de 3+ estados vale a pena documentar.

A UI (skills_quests_tab) usa `quest_state_options(flag_name)` para popular
o seletor de estado e `describe_state(flag_name, value)` para a coluna
"Descrição do Estado" do Treeview.
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Estados narrativos por flag
#
# Apenas flags com progressão de 3+ etapas precisam de entrada aqui.
# Flags binários (MetDrOwl, GazerKilled, RodrickKilled, CanSpeakToKetcheval,
# BefriendedLizardmen, ShouldFindTalismans, ConvoWithMurgo) usam o fallback
# genérico de describe_state() e não precisam de entrada.
# ---------------------------------------------------------------------------

QUEST_STATES: dict[str, dict[int, dict]] = {

    # --- MurgoFreed — arco completo de Murgo, do cativeiro à recompensa ---
    "MurgoFreed": {
        0: {"label": "Preso",
            "desc": "Murgo ainda está preso nas celas dos Dwarves no Nível 2; "
                    "o Avatar ainda não chegou até ele."},
        1: {"label": "Liberto",
            "desc": "Murgo foi libertado das celas. Ele agora vagueia livre "
                    "pelo Nível 2 e pode ser encontrado para conversas adicionais."},
        2: {"label": "Recompensa Entregue",
            "desc": "Murgo recompensou o Avatar (item ou informação) após a "
                    "libertação — fecha o arco pessoal dele."},
    },

    # --- TalkedToHagbard — introdução aos refugiados humanos ---
    "TalkedToHagbard": {
        0: {"label": "Não Encontrado",
            "desc": "O Avatar ainda não localizou Hagbard entre os refugiados "
                    "humanos no Nível 3."},
        1: {"label": "Apresentação Feita",
            "desc": "Hagbard se apresentou e explicou a situação dos refugiados "
                    "humanos, abrindo as quests da facção."},
        2: {"label": "Confiança Estabelecida",
            "desc": "Hagbard passou a confiar no Avatar e revela informações "
                    "adicionais sobre os planos de Tyball."},
    },

    # --- FindGurstang — busca pelo dwarf desaparecido ---
    "FindGurstang": {
        0: {"label": "Busca Não Iniciada",
            "desc": "O Avatar ainda não recebeu a missão de procurar Gurstang."},
        1: {"label": "Busca Ativa",
            "desc": "O Avatar foi incumbido de encontrar o dwarf desaparecido "
                    "Gurstang e está procurando por ele no Nível 2."},
        2: {"label": "Gurstang Encontrado (Vivo)",
            "desc": "Gurstang foi localizado vivo; sua situação pode ser "
                    "reportada de volta a quem pediu a busca."},
        3: {"label": "Gurstang Encontrado (Morto)",
            "desc": "Apenas o corpo ou pertences de Gurstang foram encontrados — "
                    "a busca terminou em tragédia."},
    },

    # --- WhereIsZak — localizar o mercador cego ---
    "WhereIsZak": {
        0: {"label": "Desconhecido",
            "desc": "O paradeiro de Zak, o mercador cego, ainda não foi "
                    "perguntado ou descoberto."},
        1: {"label": "Pista Obtida",
            "desc": "O Avatar obteve uma pista sobre onde Zak pode estar, "
                    "mas ainda não o encontrou pessoalmente."},
        2: {"label": "Zak Localizado",
            "desc": "Zak foi encontrado pessoalmente pelo Avatar no Nível 2."},
    },

    # --- BronusBookGoBoom — sabotagem do livro de Bronus ---
    "BronusBookGoBoom": {
        0: {"label": "Não Iniciado",
            "desc": "O Avatar ainda não recebeu o livro armadilhado ou a "
                    "missão de entrega para Bronus."},
        1: {"label": "Livro em Posse do Avatar",
            "desc": "O Avatar está carregando o livro destinado a Bronus, "
                    "mas ainda não o entregou."},
        2: {"label": "Entregue / Detonado",
            "desc": "O livro foi entregue a Bronus e o evento de sabotagem "
                    "(explosão) foi disparado, completando a quest."},
    },

    # --- KnightOfCrux — cerimônia da Ordem da Crux Gamata ---
    "KnightOfCrux": {
        0: {"label": "Não Membro",
            "desc": "O Avatar ainda não foi convidado ou iniciado na Ordem "
                    "da Crux Gamata no Nível 5."},
        1: {"label": "Provas em Andamento",
            "desc": "O Avatar foi aceito como candidato e está cumprindo as "
                    "provas exigidas pela Ordem."},
        2: {"label": "Cavaleiro da Crux Gamata",
            "desc": "O Avatar completou a cerimônia e foi nomeado Cavaleiro "
                    "da Ordem, ganhando reconhecimento e possivelmente "
                    "acesso a áreas restritas do Nível 5."},
    },

    # --- TalismansLeft — marcador narrativo de progresso da Grande Quest ---
    # Nota: NÃO confundir com playerData.talismansCollected /
    # talismansDestroyed (Sprint 10, aba Story) — este flag é um marcador
    # de *narrativa* (quais diálogos/eventos já dispararam por causa do
    # progresso), não o contador numérico real de talismãs.
    "TalismansLeft": {
        0: {"label": "Quest Não Iniciada",
            "desc": "A Grande Quest dos 8 Talismãs ainda não foi formalmente "
                    "explicada ao Avatar por nenhum NPC."},
        1: {"label": "Quest Conhecida",
            "desc": "O Avatar sabe da existência da Grande Quest, mas ainda "
                    "não progrediu o suficiente para os NPCs comentarem sobre "
                    "o progresso."},
        2: {"label": "Progresso Reconhecido",
            "desc": "NPCs relevantes já comentam sobre o progresso do Avatar "
                    "na coleta de Talismãs — diálogos de progresso médio "
                    "foram desbloqueados."},
        3: {"label": "Quase Completo",
            "desc": "Diálogos de fase final sobre os Talismãs foram "
                    "desbloqueados — a maioria já foi recuperada."},
    },

    # --- Dreams — progressão dos sonhos proféticos do Fantasma ---
    # Nota: relacionado mas distinto de playerData.dreamsRemaining[6]
    # (Sprint 10) — este flag marca *quais sonhos narrativos* já ocorreram,
    # não a contagem regressiva por talismã.
    "Dreams": {
        0: {"label": "Nenhum Sonho",
            "desc": "O Avatar ainda não teve nenhuma visão profética do "
                    "Fantasma."},
        1: {"label": "Primeiro Sonho",
            "desc": "O Avatar teve a primeira visão — geralmente um aviso "
                    "vago sobre o perigo representado por Tyball/Cabirus."},
        2: {"label": "Sonhos Recorrentes",
            "desc": "Visões adicionais ocorreram, revelando gradualmente mais "
                    "do plano do antagonista e da localização dos Talismãs."},
        3: {"label": "Visão Final",
            "desc": "O Avatar recebeu a visão culminante, geralmente "
                    "associada ao clímax da história principal."},
    },
}


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def quest_state_options(flag_name: str) -> dict[int, dict]:
    """
    Retorna {valor_inteiro: {"label", "desc"}} para o flag.

    Se o flag não tiver entrada em QUEST_STATES, retorna o fallback binário
    genérico {0: Inativo, 1: Ativo} — adequado para os flags simples
    (MetDrOwl, GazerKilled, RodrickKilled, etc.).
    """
    if flag_name in QUEST_STATES:
        return QUEST_STATES[flag_name]
    return {
        0: {"label": "Inativo", "desc": "Esta flag ainda não foi ativada."},
        1: {"label": "Ativo",   "desc": "Esta flag foi ativada (concluída/atingida)."},
    }


def describe_state(flag_name: str, value: int) -> dict:
    """
    Retorna {"label", "desc"} para o valor atual de `flag_name`.

    Valores fora do mapa conhecido (ex: um inteiro maior que o maior estado
    documentado, vindo de um save editado externamente) caem num fallback
    descritivo que ainda mostra o valor bruto, em vez de quebrar a UI.
    """
    options = quest_state_options(flag_name)
    if value in options:
        return options[value]
    max_known = max(options.keys())
    return {
        "label": f"Desconhecido ({value})",
        "desc": f"Valor {value} não documentado para esta flag "
                f"(estados conhecidos: 0–{max_known}). Pode ser um estado "
                f"válido do jogo ainda não mapeado, ou dado de um save "
                f"editado externamente.",
    }


def max_known_state(flag_name: str) -> int:
    """Retorna o maior valor de estado documentado para `flag_name`."""
    return max(quest_state_options(flag_name).keys())


def is_multi_state(flag_name: str) -> bool:
    """True se `flag_name` tem progressão narrativa de 3+ estados documentada."""
    return flag_name in QUEST_STATES and len(QUEST_STATES[flag_name]) > 2
