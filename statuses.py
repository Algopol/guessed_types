# -*- coding: utf-8 -*-

import re
from urlparse import urlparse

from helpers import StringEnum

def get_as_text(kw, field):
    """
    Return ``kw[field]`` as a stripped string
    """
    return kw.get(field, '').strip()


def strip_url_protocol(url):
    """
    Strip the protocol of an URL
    """
    if url.startswith('http://'):
        return url[7:]
    if url.startswith('https://'):
        return url[8:]
    print "Unrecognized protocol: %s" % url
    return url.split('://', 1)[-1]


class StatusVector(dict):
    """
    A status vector represents the features of a status as a dictionnary-like
    object.
    """

    KEYS = "QUMTOARWS"

    def __init__(self, *args, **kwargs):
        super(dict, self).__init__()
        for (k, v) in zip(StatusVector.KEYS, args):
            self[k] = v
        self.update(kwargs)

    def __iter__(self):
        return iter([self.get(k) for k in StatusVector.KEYS])

    def __repr__(self):
        els = ["%s=%s" % (k, self[k]) for k in StatusVector.KEYS if k in self]
        return "(%s)" % (", ".join(els))

    def __setattr__(self, k, v):
        self[k] = v

    def __getattr__(self, k):
        if k in StatusVector.KEYS:
            return self.get(k, "")
        return super(dict, self).__getattr__(k)


class ParsedStatus(object):
    """
    A ParsedStatus is a status for which we computed the features vector and
    the guessed_type.
    """

    NONGAMES_APPS = set([
        u"20minutes.fr",
        u"Actu Orange",
        u"Algopol",
        u"AlloCine",
        u"Amazon.co.uk",
        u"Amazon.fr",
        u"Articles",
        u"Avaaz.org",
        u"Birthday Cards",
        u"BlackBerry Smartphones App",
        u"Causes",
        u"Change.org",
        u"Dailymotion",
        u"Deezer",
        u"Exportateur Facebook for iPhoto",
        u"F24",
        u"Foursquare",
        u"Francetv info",
        u"Gestionnaire de Pages pour iOS",
        u"HTC Sense",
        u"HootSuite",
        u"aufeminin.com",
        u"Instagram",
        u"Jean Marc Morandini",
        u"Journal",
        u"LG Social+",
        u"Le Figaro",
        u"Le Huffington Post",
        u"Le Nouvel Observateur",
        u"Le Parisien",
        u"LeGorafi.fr",
        u"LeMonde.fr",
        u"LesInrocks.com",
        u"Liens",
        u"Maria Juana",
        u"MesOpinions.com",
        u"Microsoft",
        u"Mobile",
        u"MoviePop",
        u"Nokia",
        u"Og_likes",
        u"OverBlog",
        u"Pages Manager for Android",
        u"Pages",
        u"Pearltrees",
        u"Photos",
        u"Phrases",
        u"Pinterest",
        u"Questions",
        u"RFI Music",
        u"RTL.be",
        u"RTL.fr",
        u"Rue89",
        u"Runtastic.com",
        u"Scoop.it",
        u"Share_bookmarklet",
        u"Shazam",
        u"SongPop",
        u"Sony Ericsson Xperia",
        u"Sony Xperia™ smartphone",
        u"SonyEricsson",
        u"SoundCloud",
        u"Spotify",
        u"Status",
        u"The BBC website",
        u"The Guardian",
        u"TweetDeck",
        u"Twitter",
        u"Télérama.fr",
        u"Vidéo",
        u"Vie de merde",
        u"Vimeo",
        u"Widget Share Log App",
        u"Windows Phone",
        u"WordPress.com",
        u"YouTube",
        u"dlvr.it",
        u"i-TELE",
        u"iOS",
        u"iPhoto",
        u"le post.fr",
        u"lepoint.fr",
        u"twitterfeed",
        u"Évènements",
    ])

    NONGAMES_APPS_RE = [
        ur"^Facebook for",
        ur"^Facebook pour",
        ur"Mentions J[\u2019']aime",
        ur"^Samsung ",
    ]

    GUESSED_TYPES = StringEnum([
        'ALienSecE',
        'ALienTexteE',
        'APhotoSecheE',
        'APhotoTexteE',
        'AStatutAutre',
        'AStatutE',
        'AStatutMentionE',
        'AidentEPhoto',
        'App/Jeux',
        'ECommApp',
        'ELienChezAlter',
        'ELienSecAlter',
        'ELienSecEgo',
        'ELienSecMention',
        'ELienTexteAlter',
        'ELienTexteEgo',
        'ELienTexteMention',
        'EPhotoChezAlter',
        'EPhotoSecheAlter',
        'EPhotoSecheE',
        'EPhotoSecheEMention',
        'EPhotoSecheIdent',
        'EPhotoTexteAlter',
        'EPhotoTexteE',
        'EPhotoTexteEMention',
        'EStatutAlter',
        'EStatutChezAlter',
        'EStatutEMention',
        'EStatutEgo',
        'EVide',
        'EVideoSecheAlter',
        'EVideoSecheE',
        'EVideoSecheEMention',
        'EVideoTexteAlter',
        'EVideoTexteE',
        'EVideoTexteEMention',
        'EagitAutre',
        'EagitGroupe',
        'EaimeAutre',
        'EaimeELien',
        'EaimeEPhoto',
        'EaimeEPub',
        'EaimeEstatut',
        'EaimeLienA',
        'EaimeLienWebE',
        'EaimePage',
        'EaimePhoto',
        'EaimePublication',
        'EaimeStatut',
        'EapprouveAmi',
        'EcommAutre',
        'EcommHorsFB',
        'EcreeEvt',
        'EgoChangeBio',
        'EgoChangePP',
        'EgoCommLienAlterAlter',
        'EgoCommLienAlterEgo',
        'EgoCommLienEgoAlter',
        'EgoCommLienEgoEgo',
        'EgoCommPhotoAlterAlter',
        'EgoCommPhotoAlterEgo',
        'EgoCommPhotoEgoAlter',
        'EgoCommPhotoEgoEgo',
        'EgoCommPubAlterAlter',
        'EgoCommPubAlterEgo',
        'EgoCommPubAlterPage',
        'EgoCommPubEgoAlter',
        'EgoCommPubEgoEgo',
        'EgoCommPubEgoPage',
        'EgoCommStatutAlterAlter',
        'EgoCommStatutAlterEgo',
        'EgoCommStatutEgoAlter',
        'EgoCommStatutEgoEgo',
        'EgoCouple',
        'EidentifieEgo',
        'EindiqueFamille',
        'EpartArticle',
        'EpartAutre',
        'EpartEvtSec',
        'EpartEvtTexte',
        'EpartGroupe',
        'EpartLienA',
        'EpartLienWeb',
        'EpartPage',
        'EpartPhoto',
        'EpartPhotoTexte',
        'EpartPublication',
        'EpartStatutSec',
        'EpartStatutTexte',
        'EparticipeEvt',
        'Etweet',
        'StatutErreur',
    ])

    def __init__(self, eid, status_dict):
        """
        Create a new ParsedStatus, given the ego's ID and the status as a
        dict.
        """
        link = status_dict.get('link', {})

        self.eid = eid
        self.raw_url = link.get('link', None)
        self.url = urlparse(self.raw_url) if link and self.raw_url else None
        self.to = status_dict.get('to', [])
        self.story = status_dict.get('story', '').strip()
        self.msg = link.get('message')
        self.from_id = (status_dict.get('from') or {}).get('id')
        self.story_tags = status_dict.get('story_tags', [])
        self.tags = status_dict.get('tags', [])
        self.application = status_dict.get('application', {}).get('name')
        self.fb_type = status_dict.get('type', [])
        self.guessed_type = self.mkvector()

    def mkvector(self):
        """
        Compute the status' features vector and return its guessed_type.
        """
        GT = ParsedStatus.GUESSED_TYPES

        self.vector = StatusVector()

        if self.from_id is None:
            return GT.StatutErreur

        self.vector.Q = 'E' if self.eid == self.from_id else 'A'

        url_photo = self._match_url('www.facebook.com', '/photo.php')
        application = self.application

        # remove the msg if it's the same as the URL
        if self.msg == self.raw_url:
            self.msg = None

        self.vector.T = '1' if self.msg else '0'

        if self._match_story(ur'^\s*["«]') or \
                self.story_contains(u'à propos de la publication de') or \
                self.story_contains(u'a commenté'):
            self.vector.R = '1'
        else:
            self.vector.R = '0'

        self.story = self.story.replace(u"\u200e", "")

        self.original_story = self.story

        if re.match(ur"^ *«", self.story):
            self.story = self.story.split(u'» ')[-1]

        # (1) Apps / Games
        if self.application:
            if self.application == u"Twitter" and \
                    not self.story_contains(u"à propos de la publication de"):
                return GT.Etweet

            if self.nongame_app():
                self.application = None
            elif self.story_contains(ur"à propos de la publication de +ID"):
                return GT.ECommApp
            else:
                return GT.App_Jeux

        url_or_msg = "%s # %s" % (self.raw_url, self.msg)
        if 'apps.facebook.com' in url_or_msg or \
                ('facebook.com' in url_or_msg and 'sk=app' in url_or_msg) or \
                'facebook.com/app' in url_or_msg:
            self.vector.U = 'A'
            return GT.App_Jeux

        if self._match_story('^ID joue '):
            self.vector.A = 'J'
            return GT.App_Jeux

        if self.eid != self.from_id:
            if url_photo:
                self.vector.U = 'P'
                self.vector.O = 'P'
                if self.msg:
                    return GT.APhotoTexteE
                else:
                    return GT.APhotoSecheE

            if self.url:
                if self.msg:
                    return GT.ALienTexteE
                else:
                    return GT.ALienSecE

            # empty URL
            self.vector.U = '0'
            if self.msg:
                self.vector.W = 'E'
                return GT.AStatutE

            return GT.AStatutAutre

        if self.eid == self.from_id:
            if url_photo:
                self.vector.U = self.vector.O = 'P'
                if self.story_contains(ur"était avec +ID"):
                    self.vector.A = u"Publié"
                    return GT.EPhotoSecheIdent

                if self.story_contains(u"a publié une vidéo",
                        u"a ajouté une vidéo", u"a partagé une vidéo :"):
                    self.vector.A = u'Publié'
                    if self.msg:
                        if self.tags:
                            self.vector.M = '1'
                            return GT.EVideoTexteEMention
                        if self.to:
                            self.vector.W = 'A'
                            return GT.EVideoTexteAlter
                        # else
                        return GT.EVideoTexteE

                    # else
                    if self.tags:
                        self.vector.M = '1'
                        return GT.EVideoSecheEMention
                    if self.to:
                        self.vector.W = 'A'
                        return GT.EVideoSecheAlter

                    # else
                    return GT.EVideoSecheE

                if self.story_contains(u"a ajouté", u"a partagé un album",
                            u"a partagé une photo\.",
                            u"a publié", ur"a partagé \d+ photos\.") or not self.story:
                    self.vector.A = u'Publié'
                    if self.msg:
                        if self.tags:
                            self.vector.M = '1'
                            return GT.EPhotoTexteEMention
                        if self.to:
                            self.vector.W = 'A'
                            return GT.EPhotoTexteAlter
                        # else
                        return GT.EPhotoTexteE

                    # else
                    if self.tags:
                        self.vector.M = '1'
                        return GT.EPhotoSecheEMention
                    if self.to:
                        self.vector.W = 'A'
                        return GT.EPhotoSecheAlter

                    # else
                    return GT.EPhotoSecheE

            if self.url:
                self.vector.U = 'W'
                self.vector.O = 'L'
                if not self.story or self.story_contains(u"a publié un lien"):
                    self.vector.A = u"Publié"
                    if self.msg:
                        #if self.msg and http_in_url:
                        #    return GT.ELienTexteHTTP
                        if self.tags:
                            self.vector.M = '1'
                            return GT.ELienTexteMention
                        if self.to:
                            self.vector.W = 'A'
                            return GT.ELienTexteAlter
                        # else
                        return GT.ELienTexteEgo

                    if self.tags:
                        return GT.ELienSecMention
                    if self.to or self.story_contains(u"a publié un lien dans le [Jj]ournal de"):
                        self.vector.W = 'A'
                        return GT.ELienSecAlter
                    # else
                    return GT.ELienSecEgo


            if not self.url:
                self.vector.O = 'S'
                self.vector.A = u'Publié'
                if self.story_contains(u"a publié un lien dans le [Jj]ournal de"):
                    self.vector.O = 'L'
                    self.vector.W = 'A'
                    if application == u"Photos":
                        return GT.EPhotoChezAlter
                    return GT.ELienChezAlter

                if self.story_contains(u"à propos du [Jj]ournal de"):
                    self.vector.W = "A"
                    return GT.EStatutChezAlter
                if self.msg:
                    if self.tags:
                        self.vector.M = '1'
                        return GT.EStatutEMention
                    if self.to:
                        self.vector.W = 'A'
                        return GT.EStatutAlter
                    # else
                    return GT.EStatutEgo

                # else
                if not self.story:
                    return GT.EVide

            if self.vector.R == '1':
                if self.story_contains(u'publication'):
                    self.vector.O = 'Pub'
                    if self.story_contains(u'propre'):
                        self.vector.S = 'E'
                        if self.story_contains(u'sur le mur de'):
                            self.vector.W = 'A'
                            return GT.EgoCommPubEgoAlter
                        if self.story_contains(u'sa propre publication dans'):
                            self.vector.W = 'P'
                            return GT.EgoCommPubEgoPage
                        # else
                        self.vector.W = 'E'
                        return GT.EgoCommPubEgoEgo

                    if self.story_contains(u"à propos de la publication", \
                            u"sur la publication", "une publication"):
                        self.vector.S = 'A'
                        if self.story_contains(u"sur votre mur"):
                            self.vector.W = 'E'
                            return GT.EgoCommPubAlterEgo
                        if self.story_contains(u"sur la publication de +ID dans"):
                            self.vector.W = 'P'
                            return GT.EgoCommPubAlterPage
                        # else
                        self.vector.W = 'A'
                        return GT.EgoCommPubAlterAlter

                if self.story_contains(u'photo', u'vidéo', u'album') or \
                        self.application == "Photo":
                    self.vector.O = 'P'
                    if self.story_contains(u'propre'):
                        self.vector.S = 'E'
                        if self.story_contains(u'sur le mur de'):
                            self.vector.W = 'A'
                            return GT.EgoCommPhotoEgoAlter
                        # else
                        self.vector.W = 'E'
                        return GT.EgoCommPhotoEgoEgo

                    if self.story_contains(u"(?:à propos de|sur) (?:la photo|la vidéo|l['’]album) de",
                                           u"(?:une photo|une vidéo|un album)"):
                        self.vector.S = 'A'
                        if self.story_contains(u"sur votre mur"):
                            self.vector.W = "E"
                            return GT.EgoCommPhotoAlterEgo
                        # else
                        self.vector.W = 'A'
                        return GT.EgoCommPhotoAlterAlter

                if self.story_contains('lien'):
                    self.vector.O = 'L'
                    if self.story_contains(u'son propre lien'):
                        self.vector.S = 'E'
                        if self.story_contains(u'sur le mur de'):
                            self.vector.W = 'A'
                            return GT.EgoCommLienEgoAlter
                        # else
                        self.vector.W = 'E'
                        return GT.EgoCommLienEgoEgo

                    if self.story_contains(u'à propos du lien de', u'sur le lien de', u'un lien'):
                        self.vector.S = 'A'
                        if self.story_contains(u'sur votre mur'):
                            self.vector.W = 'E'
                            return GT.EgoCommLienAlterEgo
                        # else
                        self.vector.W = 'A'
                        return GT.EgoCommLienAlterAlter

                if self.story_contains(u'statut'):
                    self.vector.O = 'S'
                    if self.story_contains(u'propre'):
                        self.vector.S = 'E'
                        if self.story_contains(u'sur le mur de'):
                            self.vector.W = 'A'
                            return GT.EgoCommStatutEgoAlter
                        # else
                        self.vector.W = 'E'
                        return GT.EgoCommStatutEgoEgo

                    if self.story_contains(u"à propos du statut", u"sur le statut", \
                            u"un statut"):
                        self.vector.S = 'A'
                        if self.story_contains(u"sur votre mur"):
                            self.vector.W = 'E'
                            return GT.EgoCommStatutAlterEgo
                        # else
                        self.vector.W = 'A'
                        return GT.EgoCommStatutAlterAlter

                if self.story_contains(u'a commenté'):
                    self.vector.A = 'comm'
                    self.vector.W = 'Web'
                    return GT.EcommHorsFB

                return GT.EcommAutre


            if self.vector.R == '0':
                if self.story_contains(u'ID a partagé', u'ID recommande'):
                    self.vector.A = 'Partage'
                    if self.story_contains(u'lien'):
                        self.vector.O = 'Lien'
                        if self.raw_url:
                            return GT.EpartLienWeb
                        else:
                            return GT.EpartLienA

                    if self.story_contains('statut'):
                        self.vector.O = 'S'
                        if self.msg:
                            self.vector.T = '1'
                            return GT.EpartStatutTexte
                        # else
                        self.vector.T = '0'
                        return GT.EpartStatutSec

                    if self.story_contains('publication'):
                        self.vector.O = 'Pub'
                        return GT.EpartPublication

                    if self.story_contains('groupe'):
                        self.vector.O = 'Groupe'
                        return GT.EpartGroupe

                    if self.story_contains('article'):
                        self.vector.O = 'Article'
                        return GT.EpartArticle

                    if self.story_contains('page'):
                        self.vector.O = 'Page'
                        return GT.EpartPage

                    if self.story_contains(u'photo d', u'vidéo d', 'album d'):
                        self.vector.O = 'P'
                        if not self.msg:
                            return GT.EpartPhoto
                        else:
                            return GT.EpartPhotoTexte

                    if self.story_contains(u'évènement'):
                        self.vector.O = 'E'
                        if not self.msg:
                            return GT.EpartEvtSec
                        else:
                            return GT.EpartEvtTexte

                    self.vector.O = 'Z'
                    return GT.EpartAutre

                if self.story_contains(u'ID aime'):
                    self.vector.A = 'Aime'
                    if self.story_contains(u'votre photo', u'votre vidéo',
                            u'votre album'):
                        self.vector.O = 'P'
                        return GT.EaimeEPhoto

                    if self.story_contains(u'votre lien'):
                        self.vector.O = 'Lien'
                        return GT.EaimeELien

                    if self.story_contains(u'votre publication'):
                        self.vector.O = 'Pub'
                        return GT.EaimeEPub

                    if self.story_contains(u'votre statut'):
                        self.vector.O = 'S'
                        return GT.EaimeEstatut

                    if self.story_contains('statut'):
                        self.vector.O = 'S'
                        return GT.EaimeStatut

                    if self.story_contains('publication'):
                        self.vector.O = 'Pub'
                        return GT.EaimePublication

                    if self.story_contains('photo', u'vidéo', 'album'):
                        self.vector.O = 'P'
                        return GT.EaimePhoto

                    if self.story_contains(ur'ID aime +ID'):
                        self.vector.O = 'Page'
                        return GT.EaimePage

                    if self.story_contains(u'aime un lien'):
                        self.vector.O = 'Lien'
                        if not self.url:
                            return GT.EaimeLienA
                        else:
                            return GT.EaimeLienWebE

                    if self.story_contains('aime'):
                        self.vector.O = 'Z'
                        return GT.EaimeAutre

                if self.story_contains(u'a changé'):
                    self.vector.A = 'change'
                    if self.story_contains('photo de(?: son)? profil', 'photo de(?: sa)? couverture'):
                        self.vector.O = 'PP'
                        return GT.EgoChangePP

                    return GT.EgoChangeBio

                if self.story_contains(u"est passé", u"[Ff]iancé",
                        u"[Ee]n [Cc]ouple", u"[Mm]arié", u"[Cc]élibataire",
                        u"[Cc]['’]est compliqué", u"[Dd]ans une relation libre",
                        u"[Dd]ivorcé", u"[Ee]n partenariat domestique",
                        u"[Ee]n union civile", u"[Ss]éparé", u"[Vv]euf",
                        u"[Vv]euve"):
                    self.vector.O = "C"
                    return GT.EgoCouple

                if self.story_contains(u"a remplacé", u"a modifié", u"a ajouté"):
                    return GT.EgoChangeBio

                if self.story_contains(u'a été identifié'):
                    self.vector.A = 'Ident'
                    return GT.AidentEPhoto

                if self.story_contains('ami', 'amie'):
                    self.vector.A = 'Ami'
                    return GT.EapprouveAmi

                if self.story_contains(u'a indiqué'):
                    self.vector.A = u'indiqué'
                    return GT.EindiqueFamille

                if self.story_contains(u'a identifié'):
                    self.vector.A = u'identifié'
                    return GT.EindiqueFamille

                if self.story_contains('groupe'):
                    self.vector.O = 'groupe'
                    return GT.EagitGroupe

                if self.story_contains(u'a créé un évènement'):
                    self.vector.O = 'E'
                    self.vector.A = u'Publié'
                    return GT.EcreeEvt

                if self.story_contains('participe', u'a participé'):
                    self.vector.A = 'participe'
                    return GT.EparticipeEvt
                if self.story_contains(u"s['’]est elle-même",
                        u"s['’]est lui-même", ur"appara[iî]t dans"):
                    self.vector.O = 'Photo'
                    self.vector.A = 'Ident'
                    return GT.EidentifieEgo

                return GT.EagitAutre


    def _match_story(self, pattern, original=False):
        """
        Test if a story matches a given pattern. The pattern can contain
        ``ID``s, which will match any sequence of 8 hexadecimal characters.
        """
        regexp = re.sub(u'ID', u'[a-f0-9]{8}', pattern)
        # we should match on words (e.g. "\b%s\b" % pattern) but it doesn't
        # work when the pattern contains an accent
        return re.search(regexp, self.original_story if original else self.story)

    def story_contains(self, *patterns, **opts):
        """
        Test if a story match at least one pattern.
        """
        for pattern in patterns:
            if self._match_story(pattern, opts.get("original")):
                return True
        return False

    def _match_url(self, domain, path=None):
        """
        Test if this status has an URL and if the domains and paths match.
        """
        if not self.url or domain != self.url.netloc.split(':')[0]:
            return False
        return (path is None) or self.url.path == path

    def story_tags_contains(self, eid):
        """
        Test if the `story_tags` field contains the given ego id
        """
        return {"type": "user", "id": eid} in self.story_tags

    def to_contains(self, eid):
        """
        Test if the `to` field contains the given ego id
        """
        return {"id": eid} in self.to

    def nongame_app(self, app=None):
        """
        Test if this application is a non-game one (e.g. Facebook's own
        applications, media websites, etc)
        """
        if app is None:
            app = self.application
        if app is None:
            return False

        if app in ParsedStatus.NONGAMES_APPS:
            return True

        for r in ParsedStatus.NONGAMES_APPS_RE:
            if re.match(r, app):
                return True

        return False


def parse_status(eid, s):
    """
    Return a ParsedStatus object for the given status
    """
    if isinstance(s, ParsedStatus):
        return s
    return ParsedStatus(eid, s)
