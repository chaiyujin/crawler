# The constant urls of pixiv
Daily_Url = 'http://www.pixiv.net/ranking.php?mode=daily'
User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
            Chrome/54.0.2840.99 Safari/537.36'
Data_Id_Url = 'http://www.pixiv.net/member_illust.php?mode=medium&illust_id='
User_Url = 'http://www.pixiv.net/member.php?id='
Follower_List_Url = 'http://www.pixiv.net/bookmark.php?type=user&rest=show&id='
Favour_List_Url = 'http://www.pixiv.net/bookmark.php?rest=show&id='

Gallery_Url = 'https://www.pixiv.net/member_illust.php?id='
Pixiv = 'http://www.pixiv.net'

def get_gallery_url(id, page):
    url = Gallery_Url + id + '&type=all&p=' + str(page)
    return url
