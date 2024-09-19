class State:
    NONE = 0  # Pas d'état particulier
    REQUEST = 1  # Demande d'accès à la section critique
    SC = 2  # En section critique
    RELEASE = 3  # Libère la section critique