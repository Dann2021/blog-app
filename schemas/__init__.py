
from .utilisateur import (
    UtilisateurBase,
    UtilisateurCreate,
    UtilisateurUpdate,
    UtilisateurPublic,
    UtilisateurPublicAvecArticles,
    UtilisateurPublicAvecCommentaires,
    UtilisateurPublicAvecMedias,
)
from .categorie import (
    CategorieBase,
    CategorieCreate,
    CategorieUpdate,
    CategoriePublic,
    CategoriePublicAvecArticles,
)
from .tag import (
    TagBase,
    TagCreate,
    TagUpdate,
    TagPublic,
    TagPublicAvecArticle,
)
from .article import (
    ArticleBase,
    ArticleCreate,
    ArticleUpdate,
    ArticlePublic,
    ArticlePublicAvecCommentaires,
    ArticlePublicAvecTags,
    ArticlePublicAvecUtilisateur,
    ArticlePublicAvecCategorie,
)
from .commentaire import (
    CommentaireBase,
    CommentaireCreate,
    CommentaireUpdate,
    CommentairePublic,
    CommentairePublicAvecUtilisateur,
    CommentairePublicAvecArticle,
)
from .media import (
    MediaBase,
    MediaCreate,
    MediaUpdate,
    MediaPublic,
    MediaPublicAvecUtilisateur,
)
from .page import (
    PageBase,
    PageCreate,
    PageUpdate,
    PagePublic,
)
from .abonne import (
    AbonneBase,
    AbonneCreate,
    AbonneUpdate,
    AbonnePublic,
)
from .contact import (
    ContactBase,
    ContactCreate,
    ContactUpdate,
    ContactPublic,
)


UtilisateurPublicAvecArticles.model_rebuild()
UtilisateurPublicAvecCommentaires.model_rebuild()
UtilisateurPublicAvecMedias.model_rebuild()
CategoriePublicAvecArticles.model_rebuild()
TagPublicAvecArticle.model_rebuild()
ArticlePublicAvecCommentaires.model_rebuild()
ArticlePublicAvecTags.model_rebuild()
ArticlePublicAvecUtilisateur.model_rebuild()
ArticlePublicAvecCategorie.model_rebuild()
CommentairePublicAvecUtilisateur.model_rebuild()
CommentairePublicAvecArticle.model_rebuild()
MediaPublicAvecUtilisateur.model_rebuild()
