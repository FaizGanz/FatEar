#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect, flash
import pymysql.cursors
from datetime import date

#for uploading photo:
from app import app
#from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename

# ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


###Initialize the app from Flask
##app = Flask(__name__)
##app.secret_key = "secret key"

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 8889,
                       user='root',
                       password='root',
                       db='fatear',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor,
                       autocommit=False)


# def allowed_image(filename):

#     if not "." in filename:
#         return False

#     ext = filename.rsplit(".", 1)[1]

#     if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
#         return True
#     else:
#         return False


# def allowed_image_filesize(filesize):

#     if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
#         return True
#     else:
#         return False


#Define a route to hello function
@app.route('/')
def hello():
    return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM user WHERE username = %s and pwd = %s'
    cursor.execute(query, (username, password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        cursor.close()
        session['username'] = username
        return redirect(url_for('feed'))
    else:
        #returns an error message to the html page
        cursor.close()
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']
    fname = request.form['fname']
    lname = request.form['lname']
    nname = request.form['nname']
    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM user WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = '''INSERT INTO user (username, pwd, fname, lname, nickname)
                    VALUES(%s, %s, %s, %s, %s)'''
        cursor.execute(ins, (username, password, fname, lname, nname))
        conn.commit()
        cursor.close()
        return render_template('index.html')
    
@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')

#----- SEARCH MUSIC
@app.route('/search', methods=['GET', 'POST'])
def search():
    item = request.form['item']
    artist = request.form['artist']
    genre = request.form['genre']
    mar = request.form['mar']
    username = None
    rated_songs = []
    reviewed_songs = []
    rated_albums = []
    reviewed_albums = []
    # print(item, artist, genre, mar)

    cursor = conn.cursor()

    if 'username' in session:
        username = session['username']
        print('IN SESSION')
        query = '''select songID
                        from ratesong
                        where username = %s'''
        cursor.execute(query, username)
        rated_songs = cursor.fetchall()
        rated_songs = [i['songID'] for i in rated_songs]

        query = '''select songID
                        from reviewsong
                        where username = %s'''
        cursor.execute(query, username)
        reviewed_songs = cursor.fetchall()
        reviewed_songs = [i['songID'] for i in reviewed_songs]

        query = '''select albumID
                        from ratealbum
                        where username = %s'''
        cursor.execute(query, username)
        rated_albums = cursor.fetchall()
        rated_albums = [i['albumID'] for i in rated_albums]

        query = '''select albumID
                        from reviewalbum
                        where username = %s'''
        cursor.execute(query, username)
        reviewed_albums = cursor.fetchall()
        reviewed_albums = [i['albumID'] for i in reviewed_albums]

    

    if item != '':
        if (artist != '' and genre != '' and mar != ''):
            query = '''select distinct songID, songURL, title, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where title = %s and genre = %s and fname = %s and songID in (
                        select songID
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join ratesong
                        natural join artistperformssong
                        natural join artist
                        group by songID
                        having avg(stars) >= %s)'''
            cursor.execute(query, (item, genre, artist, mar))
            songs = cursor.fetchall()
            query = '''select distinct albumID, albumURL, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where albumName = %s and genre = %s and fname = %s and albumID in (
                        select albumID
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join ratealbum
                        natural join artistperformssong
                        natural join artist
                        group by albumID
                        having avg(stars) >= %s)'''
            cursor.execute(query, (item, genre, artist, mar))
            albums = cursor.fetchall()
            cursor.close()
            return render_template('search.html', 
                                   songs = songs, 
                                   albums=albums, 
                                   n=len(songs), 
                                   m=len(albums),
                                   username = username,
                                   rated_songs = rated_songs,
                                   reviewed_songs = reviewed_songs,
                                   rated_albums = rated_albums,
                                   reviewed_albums = reviewed_albums)
        
        if (artist != '' and genre != ''):
            query = '''select distinct songID, songURL, title, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where title = %s and fname = %s and genre = %s'''
            cursor.execute(query, (item, artist, genre))
            songs = cursor.fetchall()
            query = '''select distinct albumID, albumURL, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where albumName = %s and fname= %s and genre = %s'''
            cursor.execute(query, (item, artist, genre))
            albums = cursor.fetchall()
            cursor.close()
            return render_template('search.html', 
                                   songs = songs, 
                                   albums=albums, 
                                   n=len(songs), 
                                   m=len(albums),
                                   username = username,
                                   rated_songs = rated_songs,
                                   reviewed_songs = reviewed_songs,
                                   rated_albums = rated_albums,
                                   reviewed_albums = reviewed_albums)
        
        if (artist != '' and mar != ''):
            query = '''select distinct songID, songURL, title, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where title = %s and fname = %s and songID in (
                        select songID
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join ratesong
                        natural join artistperformssong
                        natural join artist
                        group by songID
                        having avg(stars) >= %s)'''
            cursor.execute(query, (item, artist, mar))
            songs = cursor.fetchall()
            query = '''select distinct albumID, albumURL, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where albumName = %s and fname = %s and albumID in (
                        select albumID
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join ratealbum
                        natural join artistperformssong
                        natural join artist
                        group by albumID
                        having avg(stars) >= %s)'''
            cursor.execute(query, (item, artist, mar))
            albums = cursor.fetchall()
            cursor.close()
            return render_template('search.html', 
                                   songs = songs, 
                                   albums=albums, 
                                   n=len(songs), 
                                   m=len(albums),
                                   username = username,
                                   rated_songs = rated_songs,
                                   reviewed_songs = reviewed_songs,
                                   rated_albums = rated_albums,
                                   reviewed_albums = reviewed_albums)
        
        if (genre != '' and mar != ''):
            query = '''select distinct songID, songURL, title, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where title = %s and genre = %s and songID in (
                        select songID
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join ratesong
                        natural join artistperformssong
                        natural join artist
                        group by songID
                        having avg(stars) >= %s)'''
            cursor.execute(query, (item, genre, mar))
            songs = cursor.fetchall()
            query = '''select distinct albumID, albumURL, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where albumName = %s and genre = %s and albumID in (
                        select albumID
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join ratealbum
                        natural join artistperformssong
                        natural join artist
                        group by albumID
                        having avg(stars) >= %s)'''
            cursor.execute(query, (item, genre, mar))
            albums = cursor.fetchall()
            cursor.close()
            return render_template('search.html', 
                                   songs = songs, 
                                   albums=albums, 
                                   n=len(songs), 
                                   m=len(albums),
                                   username = username,
                                   rated_songs = rated_songs,
                                   reviewed_songs = reviewed_songs,
                                   rated_albums = rated_albums,
                                   reviewed_albums = reviewed_albums)
        
        if artist != '':
            query = '''select distinct songID, songURL, title, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where title = %s and fname = %s'''
            cursor.execute(query, (item, artist))
            songs = cursor.fetchall()
            query = '''select distinct albumID, albumURL, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where albumName = %s and fname= %s'''
            cursor.execute(query, (item, artist))
            albums = cursor.fetchall()
            cursor.close()
            return render_template('search.html', 
                                   songs = songs, 
                                   albums=albums, 
                                   n=len(songs), 
                                   m=len(albums),
                                   username = username,
                                   rated_songs = rated_songs,
                                   reviewed_songs = reviewed_songs,
                                   rated_albums = rated_albums,
                                   reviewed_albums = reviewed_albums)
        
        if genre != '':
            query = '''select distinct songID, songURL, title, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where title = %s and genre = %s'''
            cursor.execute(query, (item, genre))
            songs = cursor.fetchall()
            query = '''select distinct albumID, albumURL, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where albumName = %s and genre= %s'''
            cursor.execute(query, (item, genre))
            albums = cursor.fetchall()
            cursor.close()
            return render_template('search.html', 
                                   songs = songs, 
                                   albums=albums, 
                                   n=len(songs), 
                                   m=len(albums),
                                   username = username,
                                   rated_songs = rated_songs,
                                   reviewed_songs = reviewed_songs,
                                   rated_albums = rated_albums,
                                   reviewed_albums = reviewed_albums)
        
        if mar != '':
            query = '''select distinct songID, songURL, title, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where title = %s and songID in (
                        select songID
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join ratesong
                        natural join artistperformssong
                        natural join artist
                        group by songID
                        having avg(stars) >= %s)'''
            cursor.execute(query, (item, mar))
            songs = cursor.fetchall()
            query = '''select distinct albumID, albumURL, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where albumName = %s and albumID in (
                        select albumID
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join ratealbum
                        natural join artistperformssong
                        natural join artist
                        group by albumID
                        having avg(stars) >= %s)'''
            cursor.execute(query, (item, mar))
            albums = cursor.fetchall()
            cursor.close()
            return render_template('search.html', 
                                   songs = songs, 
                                   albums=albums, 
                                   n=len(songs), 
                                   m=len(albums),
                                   username = username,
                                   rated_songs = rated_songs,
                                   reviewed_songs = reviewed_songs,
                                   rated_albums = rated_albums,
                                   reviewed_albums = reviewed_albums)
        
        if (artist == '' and genre == '' and mar == ''):
            query = '''select distinct songID, songURL, title, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where title = %s'''
            cursor.execute(query, item)
            songs = cursor.fetchall()
            query = '''select distinct albumID, albumURL, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where albumName = %s'''
            cursor.execute(query, item)
            albums = cursor.fetchall()
            cursor.close()
            return render_template('search.html', 
                                   songs = songs, 
                                   albums=albums, 
                                   n=len(songs), 
                                   m=len(albums),
                                   username = username,
                                   rated_songs = rated_songs,
                                   reviewed_songs = reviewed_songs,
                                   rated_albums = rated_albums,
                                   reviewed_albums = reviewed_albums)
    

    # NO ITEM
    if item == '':
        if (artist != '' and genre != '' and mar != ''):
            query = '''select distinct songID, songURL, title, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where genre = %s and fname = %s and songID in (
                        select songID
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join ratesong
                        natural join artistperformssong
                        natural join artist
                        group by songID
                        having avg(stars) >= %s)'''
            cursor.execute(query, (genre, artist, mar))
            songs = cursor.fetchall()
            query = '''select distinct albumID, albumURL, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where genre = %s and fname = %s and albumID in (
                        select albumID
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join ratealbum
                        natural join artistperformssong
                        natural join artist
                        group by albumID
                        having avg(stars) >= %s)'''
            cursor.execute(query, (genre, artist, mar))
            albums = cursor.fetchall()
            cursor.close()
            return render_template('search.html', 
                                   songs = songs, 
                                   albums=albums, 
                                   n=len(songs), 
                                   m=len(albums),
                                   username = username,
                                   rated_songs = rated_songs,
                                   reviewed_songs = reviewed_songs,
                                   rated_albums = rated_albums,
                                   reviewed_albums = reviewed_albums)
            
        if (artist != '' and genre != ''):
            query = '''select distinct songID, songURL, title, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where fname = %s and genre = %s'''
            cursor.execute(query, (artist, genre))
            songs = cursor.fetchall()
            query = '''select distinct albumID, albumURL, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where fname= %s and genre = %s'''
            cursor.execute(query, (artist, genre))
            albums = cursor.fetchall()
            cursor.close()
            return render_template('search.html', 
                                   songs = songs, 
                                   albums=albums, 
                                   n=len(songs), 
                                   m=len(albums),
                                   username = username,
                                   rated_songs = rated_songs,
                                   reviewed_songs = reviewed_songs,
                                   rated_albums = rated_albums,
                                   reviewed_albums = reviewed_albums)
        
        if (artist != '' and mar != ''):
            query = '''select distinct songID, songURL, title, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where fname = %s and songID in (
                        select songID
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join ratesong
                        natural join artistperformssong
                        natural join artist
                        group by songID
                        having avg(stars) >= %s)'''
            cursor.execute(query, (artist, mar))
            songs = cursor.fetchall()
            query = '''select distinct albumID, albumURL, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where fname = %s and albumID in (
                        select albumID
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join ratealbum
                        natural join artistperformssong
                        natural join artist
                        group by albumID
                        having avg(stars) >= %s)'''
            cursor.execute(query, (artist, mar))
            albums = cursor.fetchall()
            cursor.close()
            return render_template('search.html', 
                                   songs = songs, 
                                   albums=albums, 
                                   n=len(songs), 
                                   m=len(albums),
                                   username = username,
                                   rated_songs = rated_songs,
                                   reviewed_songs = reviewed_songs,
                                   rated_albums = rated_albums,
                                   reviewed_albums = reviewed_albums)

        if (genre != '' and mar != ''):
            query = '''select distinct songID, songURL, title, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where genre = %s and songID in (
                        select songID
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join ratesong
                        natural join artistperformssong
                        natural join artist
                        group by songID
                        having avg(stars) >= %s)'''
            cursor.execute(query, (genre, mar))
            songs = cursor.fetchall()
            query = '''select distinct albumID, albumURL, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where genre = %s and albumID in (
                        select albumID
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join ratealbum
                        natural join artistperformssong
                        natural join artist
                        group by albumID
                        having avg(stars) >= %s)'''
            cursor.execute(query, (genre, mar))
            albums = cursor.fetchall()
            cursor.close()
            return render_template('search.html', 
                                   songs = songs, 
                                   albums=albums, 
                                   n=len(songs), 
                                   m=len(albums),
                                   username = username,
                                   rated_songs = rated_songs,
                                   reviewed_songs = reviewed_songs,
                                   rated_albums = rated_albums,
                                   reviewed_albums = reviewed_albums)

        if artist != '':
            query = '''select distinct songID, songURL, title, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where fname = %s'''
            cursor.execute(query, artist)
            songs = cursor.fetchall()
            query = '''select distinct albumID, albumURL, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where fname= %s'''
            cursor.execute(query, artist)
            albums = cursor.fetchall()
            cursor.close()
            return render_template('search.html', 
                                   songs = songs, 
                                   albums=albums, 
                                   n=len(songs), 
                                   m=len(albums),
                                   username = username,
                                   rated_songs = rated_songs,
                                   reviewed_songs = reviewed_songs,
                                   rated_albums = rated_albums,
                                   reviewed_albums = reviewed_albums)
        
        if genre != '':
            query = '''select distinct songID, songURL, title, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where genre = %s'''
            cursor.execute(query, genre)
            songs = cursor.fetchall()
            query = '''select distinct albumID, albumURL, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where genre= %s'''
            cursor.execute(query, genre)
            albums = cursor.fetchall()
            cursor.close()
            return render_template('search.html', 
                                   songs = songs, 
                                   albums=albums, 
                                   n=len(songs), 
                                   m=len(albums),
                                   username = username,
                                   rated_songs = rated_songs,
                                   reviewed_songs = reviewed_songs,
                                   rated_albums = rated_albums,
                                   reviewed_albums = reviewed_albums)
        
        if mar != '':
            query = '''select distinct songID, songURL, title, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where songID in (
                        select songID
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join ratesong
                        natural join artistperformssong
                        natural join artist
                        group by songID
                        having avg(stars) >= %s)'''
            cursor.execute(query, mar)
            songs = cursor.fetchall()
            query = '''select distinct albumID, albumURL, fname, albumName
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join artistperformssong
                        natural join artist
                        where albumID in (
                        select albumID
                        from song 
                        natural join songgenre
                        natural join songinalbum
                        natural join album
                        natural join ratealbum
                        natural join artistperformssong
                        natural join artist
                        group by albumID
                        having avg(stars) >= %s)'''
            cursor.execute(query, mar)
            albums = cursor.fetchall()
            cursor.close()
            return render_template('search.html', 
                                   songs = songs, 
                                   albums=albums, 
                                   n=len(songs), 
                                   m=len(albums),
                                   username = username,
                                   rated_songs = rated_songs,
                                   reviewed_songs = reviewed_songs,
                                   rated_albums = rated_albums,
                                   reviewed_albums = reviewed_albums)

    cursor.close()
    return render_template('index.html')


#----- NEW FEED
@app.route('/feed')
def feed():
    username = session['username']
    cursor = conn.cursor()
    query = '''select * from (
                select f.follows, r.reviewText, a.albumName, a.albumURL, r.reviewDate, j.fname
                    from user as u 
                    join follows as f on (u.username = f.follower)
                    join reviewAlbum as r on (f.follows = r.username)
                    natural join album as a
                    natural join songinalbum as g
                    natural join artistperformssong as h
                    join artist as j on (h.artistID = j.artistID)
                    where u.username = %s and u.lastlogin < r.reviewDate
                union
                select f.friend_name, r.reviewText, a.albumName, a.albumURL, r.reviewDate, j.fname
                from user as u, 
                (select 
                case
                    when user1 = %s then user2
                    else user1
                end as friend_name
                from friend
                where (user1 = %s or user2 = %s) and acceptStatus = 'Accepted') as f
                join reviewAlbum as r on (f.friend_name = r.username)
                natural join album as a
                natural join songinalbum as g
                natural join artistperformssong as h
                join artist as j on (h.artistID = j.artistID)
                where u.username = %s and u.lastlogin < r.reviewDate) as nt order by reviewDate desc'''
    cursor.execute(query, (username, username, username, username, username))
    data1 = cursor.fetchall()
    query = '''select * from (
                select f.follows, t.reviewText, s.title, s.songURL, t.reviewDate, j.fname, a.albumName
                from user as u 
                join follows as f on (u.username = f.follower)
                join reviewSong as t on (f.follows = t.username)
                natural join song as s
                natural join artistperformssong as g
                join artist as j on (g.artistID = j.artistID)
                natural join songinalbum as h
                natural join album as a
                where u.username = %s and u.lastlogin < t.reviewDate
                union
                select f.friend_name, t.reviewText, s.title, s.songURL, t.reviewDate, j.fname, a.albumName
                from user as u, 
                (select 
                case
                    when user1 = %s then user2
                    else user1
                end as friend_name
                from friend
                where (user1 = %s or user2 = %s) and acceptStatus = 'Accepted') as f
                join reviewSong as t on (f.friend_name = t.username)
                natural join song as s
                natural join artistperformssong as g
                join artist as j on (g.artistID = j.artistID)
                natural join songinalbum as h
                natural join album as a
                where u.username = %s and u.lastlogin < t.reviewDate) as nt order by reviewDate desc'''
    cursor.execute(query, (username, username, username, username, username))
    data2 = cursor.fetchall()
    today = date.today()
    # query = '''select distinct title, albumName, fname
    #             from song
    #             natural join songinalbum
    #             natural join artistperformsong
    #             natural join artist
    #             natural join userfanofartist
    #             where username = %s and releaseDate <= %s'''
    # cursor.execute(query, (username, today))
    # data3 = cursor.fetchall()
    query = 'UPDATE user SET lastlogin = %s WHERE username = %s'
    cursor.execute(query, (today, username)) #2022-03-26
    cursor.close()
    return render_template('feed.html',
                            username=username,
                            albumReviews=data1,
                            songReviews=data2,
                            no_albums=len(data1),
                            no_songs=len(data2)
                            )

#----- HOME
@app.route('/home')
def home():
    user = session['username']
    cursor = conn.cursor();
    query = '''select * from (
                select distinct f.follows, r.reviewText, a.albumName, a.albumURL, r.reviewDate, j.fname
                    from user as u 
                    join follows as f on (u.username = f.follower)
                    join reviewAlbum as r on (f.follows = r.username)
                    natural join album as a
                    natural join songinalbum as g
                    natural join artistperformssong as h
                    join artist as j on (h.artistID = j.artistID)
                    where u.username = %s
                union
                select distinct f.friend_name, r.reviewText, a.albumName, a.albumURL, r.reviewDate, j.fname
                from user as u, 
                (select 
                case
                    when user1 = %s then user2
                    else user1
                end as friend_name
                from friend
                where (user1 = %s or user2 = %s) and acceptStatus = 'Accepted') as f
                join reviewAlbum as r on (f.friend_name = r.username)
                natural join album as a
                natural join songinalbum as g
                natural join artistperformssong as h
                join artist as j on (h.artistID = j.artistID)
                where u.username = %s) as nt order by reviewDate desc'''
    cursor.execute(query, (user, user, user, user, user))
    data1 = cursor.fetchall()
    query = '''select * from (
                select distinct f.follows, t.reviewText, s.title, s.songURL, t.reviewDate, j.fname, a.albumName
                from user as u 
                join follows as f on (u.username = f.follower)
                join reviewSong as t on (f.follows = t.username)
                natural join song as s
                natural join artistperformssong as g
                join artist as j on (g.artistID = j.artistID)
                natural join songinalbum as h
                natural join album as a
                where u.username = %s
                union
                select distinct f.friend_name, t.reviewText, s.title, s.songURL, t.reviewDate, j.fname, a.albumName
                from user as u, 
                (select 
                case
                    when user1 = %s then user2
                    else user1
                end as friend_name
                from friend
                where (user1 = %s or user2 = %s) and acceptStatus = 'Accepted') as f
                join reviewSong as t on (f.friend_name = t.username)
                natural join song as s
                natural join artistperformssong as g
                join artist as j on (g.artistID = j.artistID)
                natural join songinalbum as h
                natural join album as a
                where u.username = %s) as nt order by reviewDate desc'''
    cursor.execute(query, (user, user, user, user, user))
    data2 = cursor.fetchall()
    cursor.close()
    return render_template('home.html', 
                           username=user, 
                           albumReviews=data1, 
                           songReviews=data2,
                           n=len(data1),
                           m=len(data2))

#---- Show other users
@app.route('/show_user', methods=["GET", "POST"])
def show_user():
    user = request.args['user']
    cursor = conn.cursor()
    query = '''SELECT title, songURL, albumName, fname, reviewText, reviewDate 
                FROM reviewSong 
                NATURAL JOIN song 
                natural join artistperformssong
                natural join artist
                natural join songinalbum
                natural join album
                WHERE username = %s 
                ORDER BY reviewDate DESC'''
    cursor.execute(query, user)
    songs = cursor.fetchall()
    query = '''SELECT distinct albumName, albumURL, fname, reviewText, reviewDate 
                FROM reviewAlbum 
                NATURAL JOIN album 
                natural join songinalbum
                natural join song
                natural join artistperformssong
                natural join artist
                WHERE username = %s 
                ORDER BY reviewDate DESC'''
    cursor.execute(query, user)
    albums = cursor.fetchall()
    cursor.close()
    return render_template('show_user.html', 
                           user=user, 
                           songs=songs,
                           albums=albums,
                           n=len(songs),
                           m=len(albums))

#----- EDIT or DELETE REVIEWS


@app.route('/edit_rating')
def edit_rating():
    username = session['username']
    status = request.args['rating_status']
    print(status)
    if 'albumID' in request.args:
        albumID = request.args['albumID']
        cursor = conn.cursor()
        if status == 'update':
            query = '''select distinct albumName, fname, stars
                        from rateAlbum
                        natural join album
                        natural join songinalbum
                        natural join artistperformssong
                        natural join artist
                        where username = %s and albumID = %s'''
            cursor.execute(query, (username, albumID))
            item = cursor.fetchone()
        else:
            query = '''select distinct albumName, fname,
                        from album
                        natural join songinalbum
                        natural join artistperformssong
                        natural join artist
                        where albumID = %s'''
            cursor.execute(query, albumID)
            item = cursor.fetchone()
        cursor.close()
        return render_template('edit_rating.html',
                               username = username,
                               item = item,
                               tp = "album",
                               id = albumID,
                               status = status)
    elif 'songID' in request.args:
        songID = request.args['songID']
        cursor = conn.cursor()
        if status == 'update':
            query = '''select title, albumName, fname, stars
                        from rateSong 
                        natural join song
                        natural join artistperformssong
                        natural join artist
                        natural join songinalbum
                        natural join album
                        where username = %s and songID = %s'''
            cursor.execute(query, (username, songID))
            item = cursor.fetchone()
        else:
            query = '''select title, albumName, fname
                        from song
                        natural join artistperformssong
                        natural join artist
                        natural join songinalbum
                        natural join album
                        where songID = %s'''
            cursor.execute(query, songID)
            item = cursor.fetchone()

        cursor.close()
        return render_template('edit_rating.html',
                               username = username,
                               item = item,
                               tp = "song",
                               id = songID,
                               status = status)
    
@app.route('/post_rating')
def post_rating():
    username = session['username']
    text = request.args['text']
    id = request.args['id']
    cursor = conn.cursor()
    if request.args['status'] == 'update':
        if request.args['tp'] == 'album':
            query = '''update rateAlbum
                        set stars = %s
                        where username = %s and albumID = %s'''
            cursor.execute(query, (text, username, id))
        elif request.args['tp'] == 'song':
            query = '''update rateSong
                        set stars = %s
                        where username = %s and songID = %s'''
            cursor.execute(query, (text, username, id))
    elif request.args['status'] == 'create':
        today = date.today()
        if request.args['tp'] == 'album':
            query = '''insert into rateAlbum (username, albumID, stars)
                        values (%s, %s, %s)'''
            cursor.execute(query, (username, id, text))
        elif request.args['tp'] == 'song':
            query = '''insert into rateSong (username, songID, stars, ratingDate)
                        values (%s, %s, %s, %s)'''
            cursor.execute(query, (username, id, text, today))
    conn.commit()
    cursor.close()
    return redirect(url_for('profile'))

@app.route('/edit_review')
def edit_review():
    username = session['username']
    status = request.args['review_status']
    print(status)
    if 'albumID' in request.args:
        albumID = request.args['albumID']
        cursor = conn.cursor()
        if status == 'update':
            query = '''select distinct albumName, fname, reviewDate, reviewText
                        from reviewAlbum
                        natural join album
                        natural join songinalbum
                        natural join artistperformssong
                        natural join artist
                        where username = %s and albumID = %s'''
            cursor.execute(query, (username, albumID))
            item = cursor.fetchone()
        else:
            query = '''select distinct albumName, fname
                        from album 
                        natural join songinalbum
                        natural join artistperformssong
                        natural join artist
                        where albumID = %s'''
            cursor.execute(query, albumID)
            item = cursor.fetchone()
        cursor.close()
        return render_template('edit_review.html',
                               username = username,
                               item = item,
                               tp = "album",
                               id = albumID,
                               status = status)
    elif 'songID' in request.args:
        songID = request.args['songID']
        cursor = conn.cursor()
        if status == 'update':
            query = '''select reviewText, reviewDate, title, albumName, fname
                        from reviewSong 
                        natural join song
                        natural join artistperformssong
                        natural join artist
                        natural join songinalbum
                        natural join album
                        where username = %s and songID = %s'''
            cursor.execute(query, (username, songID))
            item = cursor.fetchone()
        else:
            query = '''select title, albumName, fname
                        from song
                        natural join artistperformssong
                        natural join artist
                        natural join songinalbum
                        natural join album
                        where songID = %s'''
            cursor.execute(query, songID)
            item = cursor.fetchone()
        cursor.close()
        return render_template('edit_review.html',
                               username = username,
                               item = item,
                               tp = "song",
                               id = songID,
                               status = status)

@app.route('/post_review')
def post_review():
    username = session['username']
    text = request.args['text']
    id = request.args['id']
    cursor = conn.cursor()
    if request.args['status'] == 'update':
        if request.args['tp'] == 'album':
            query = '''update reviewAlbum
                        set reviewText = %s
                        where username = %s and albumID = %s'''
            cursor.execute(query, (text, username, id))
        elif request.args['tp'] == 'song':
            query = '''update reviewSong
                        set reviewText = %s
                        where username = %s and songID = %s'''
            cursor.execute(query, (text, username, id))
    elif request.args['status'] == 'create':
        today = date.today()
        if request.args['tp'] == 'album':
            query = '''insert into reviewAlbum (username, albumID, reviewText, reviewDate)
                        values (%s, %s, %s, %s)'''
            cursor.execute(query, (username, id, text, today))
        elif request.args['tp'] == 'song':
            query = '''insert into reviewSong (username, songID, reviewText, reviewDate)
                        values (%s, %s, %s, %s)'''
            cursor.execute(query, (username, id, text, today))

    cursor.close()
    return redirect(url_for('profile'))

@app.route('/delete_review')
def delete():
    username = session['username']
    if 'albumID' in request.args:
        albumID = request.args['albumID']
        cursor = conn.cursor()
        query = '''delete from reviewAlbum
                    where username = %s and albumID = %s'''
        cursor.execute(query, (username, albumID))
    elif 'songID' in request.args:
        songID = request.args['songID']
        cursor = conn.cursor()
        query = '''delete from reviewSong
                    where username = %s and songID = %s'''
        cursor.execute(query, (username, songID))

    return redirect(url_for('profile'))

#----- PROFILE
@app.route('/profile')
def profile():
    username = session['username']
    cursor = conn.cursor()
    query = '''select distinct albumID, albumName, albumURL, reviewText, reviewDate, fname
                from reviewAlbum 
                natural join album
                natural join songinalbum
                natural join artistperformssong
                natural join artist
                where username = %s
                order by reviewDate desc'''
    cursor.execute(query, (username))
    albumReviews = cursor.fetchall()
    query = '''select songID, title, songURL, reviewText, reviewDate, albumName, fname
                from reviewSong natural join song
                natural join artistperformssong
                natural join artist
                natural join songinalbum
                natural join album
                where username = %s
                order by reviewDate desc'''
    cursor.execute(query, (username))
    songReviews = cursor.fetchall()
    cursor.close()
    return render_template('profile.html', 
                           username=username, 
                           albumReviews=albumReviews, 
                           songReviews=songReviews,
                           n=len(albumReviews),
                           m=len(songReviews))


#----- FRIENDS
@app.route('/friends')
def friends():
    username = session['username']
    cursor = conn.cursor()
    query = '''select 
                case
	                when user1 = %s then user2
	                else user1
                end as friend_name
                from friend
                where (user1 = %s or user2 = %s) and acceptStatus = %s'''
    cursor.execute(query, (username, username, username, "Accepted"))
    data = cursor.fetchall()
    cursor.close()
    return render_template('friends.html', user_list=data, n=len(data))

@app.route('/remove_friend')
def remove_friend():
    username = session['username']
    user = request.args['user']
    cursor = conn.cursor()
    query = '''delete from friend
                where ((user1 = %s and user2 = %s) 
                or (user1 = %s and user2 = %s)) 
                and acceptStatus = %s'''
    
    cursor.execute(query, (username, user, user, username, "Accepted"))
    cursor.close()
    return redirect(url_for('friends'))

#----- Friend requests
@app.route('/friend_requests')
def friend_requests():
    username = session['username']
    cursor = conn.cursor()
    query = '''select 
                case
	                when user1 = %s then user2
	                else user1
                end as friend_name
                from friend
                where (user1 = %s or user2 = %s) and acceptStatus = %s and requestSentBy <> %s'''
    cursor.execute(query, (username, username, username, "Pending", username))
    data = cursor.fetchall()
    cursor.close()
    return render_template('friend_requests.html', user_list=data, n=len(data))

@app.route('/accept_friendship')
def accept_friendship():
    username = session['username']
    user = request.args['user']
    cursor = conn.cursor()
    query = '''update friend
                set acceptStatus = "Accepted"
                where ((user1 = %s and user2 = %s) 
                or (user1 = %s and user2 = %s)) 
                and acceptStatus = "Pending"
                and requestSentBy = %s'''
    
    cursor.execute(query, (username, user, user, username, user))
    cursor.close()
    return redirect(url_for('friend_requests'))

@app.route('/decline_friendship')
def decline_friendship():
    username = session['username']
    user = request.args['user']
    cursor = conn.cursor()
    query = '''update friend
                set acceptStatus = "Not Accepted"
                where ((user1 = %s and user2 = %s) 
                or (user1 = %s and user2 = %s)) 
                and acceptStatus = "Pending"
                and requestSentBy = %s'''
    
    cursor.execute(query, (username, user, user, username, user))
    cursor.close()
    return redirect(url_for('friend_requests'))

#----- Request Friendship
@app.route('/request_friendship')
def request_friendship():
    username = session['username']
    user = request.args['user']
    cursor = conn.cursor()
    query = '''select user1 
                from friend
                where user1 = %s and user2 = %s and acceptStatus = %s'''
    cursor.execute(query, (username, user, "Not Accepted"))
    data = cursor.fetchall()
    if len(data) != 0:
         query = '''delete 
                    from friend
                    where user1 = %s and user2 = %s and acceptStatus = %s'''
         cursor.execute(query, (username, user, "Not Accepted"))
    query = '''insert into friend (user1, user2, acceptStatus, requestSentBy)
                values (%s, %s, %s, %s)'''
    cursor.execute(query, (username, user, "Pending", username))
    cursor.close()
    return redirect(url_for('profile'))

@app.route('/remove_request')
def remove_request():
    username = session['username']
    user = request.args['user']
    cursor = conn.cursor()
    query = "delete from friend where user1 = %s and user2 = %s and acceptStatus = %s"
    cursor.execute(query, (username, user, "Pending"))
    cursor.close()
    return redirect(url_for('profile'))


#----- FOLLOWING
@app.route('/followers')
def followers():
    username = session['username']
    cursor = conn.cursor()
    query = '''select follower
                from follows
                where follows = %s'''
    cursor.execute(query, (username))
    data = cursor.fetchall()
    cursor.close()
    return render_template('followers.html', user_list=data, n=len(data))

@app.route('/remove_follower')
def remove_follower():
    username = session['username']
    user = request.args['user']
    cursor = conn.cursor()
    query = '''delete from follows
                where follower = %s and follows = %s'''
    cursor.execute(query, (user, username))
    cursor.close()
    return redirect(url_for('followers'))

@app.route('/following')
def following():
    username = session['username']
    cursor = conn.cursor()
    query = '''select follows
                from follows
                where follower = %s'''
    cursor.execute(query, (username))
    data = cursor.fetchall()
    cursor.close()
    return render_template('following.html', user_list=data, n=len(data))

@app.route('/follow')
def follow():
    username = session['username']
    user = request.args['user']
    cursor = conn.cursor();
    query = '''insert into follows (follower, follows)
                values (%s, %s)'''
    cursor.execute(query, (username, user))
    cursor.close()
    return redirect(url_for('following'))

@app.route('/unfollow')
def unfollow():
    username = session['username']
    user = request.args['user']
    cursor = conn.cursor();
    query = '''delete from follows
                where follower = %s and follows = %s'''
    cursor.execute(query, (username, user))
    cursor.close()
    return redirect(url_for('following'))


#----- FIND USERS
@app.route('/find_users', methods=['GET', 'POST'])
def find_users():
    username = session['username']
    user = request.form['user']
    cursor = conn.cursor();
    query = '''select username from user where username like %s'''
    cursor.execute(query, ('%' + user +'%'))
    users = cursor.fetchall()
    query = '''select 
                case
	                when user1 = %s then user2
	                else user1
                end as friend_name
                from friend
                where (user1 = %s or user2 = %s) and acceptStatus = %s'''
    cursor.execute(query, (username, username, username, "Accepted"))
    friends = cursor.fetchall()
    friends = [i['friend_name'] for i in friends]
    query = '''select 
                case
	                when user1 = %s then user2
	                else user1
                end as friend_name
                from friend
                where (user1 = %s or user2 = %s) and acceptStatus = %s and requestSentBy = %s'''
    cursor.execute(query, (username, username, username, "Pending", username))
    pending = cursor.fetchall()
    pending = [i['friend_name'] for i in pending]
    query = '''select follows
                from follows
                where follower = %s'''
    cursor.execute(query, (username))
    follows = cursor.fetchall()
    follows = [i['follows'] for i in follows]
    cursor.close()
    return render_template('find_users.html',
                           username=username,
                           results=len(users),
                           users = users,
                           friends=friends,
                           pending=pending,
                           follows=follows)

#----- FIND ARTISTS

@app.route('/find_artists', methods=['GET', 'POST'])
def find_artists():
    username = session['username']
    artist = request.form['artist']
    cursor = conn.cursor()
    query = '''select artistID, fname from artist where fname like %s'''
    cursor.execute(query, ('%' + artist +'%'))
    artists = cursor.fetchall()
    query = '''select artistID
                from userfanofartist
                where username = %s'''
    cursor.execute(query, username)
    fanof = cursor.fetchall()
    fanof = [i['artistID'] for i in fanof]
    cursor.close()
    return render_template('find_artists.html',
                           n=len(artists),
                           artists = artists,
                           fanof=fanof)

@app.route('/view_artist', methods=['GET', 'POST'])
def view_artist():
    username = session['username']
    artistID = request.form['artistID']
    cursor = conn.cursor()
    query = '''select distinct title, songURL, albumName
                from song
                natural join artistperformssong
                natural join songinalbum
                natural join album
                where artistID = %s'''
    cursor.execute(query, artistID)
    songs = cursor.fetchall()
    query = '''select distinct albumName, albumURL
                from song
                natural join artistperformssong
                natural join songinalbum
                natural join album
                where artistID = %s'''
    cursor.execute(query, artistID)
    albums = cursor.fetchall()
    query = '''select fname, artistBio, artistURL
                from artist
                where artistID = %s'''
    cursor.execute(query, artistID)
    artist = cursor.fetchone()
    cursor.close()

    return render_template('view_artist.html',
                           artist = artist,
                           songs = songs,
                           albums = albums,
                           artistID = artistID)

@app.route('/fan', methods=['GET', 'POST'])
def fan():
    username = session['username']
    artistID = request.form['artistID']
    cursor = conn.cursor()
    query = '''insert into userfanofartist (username, artistID)
                values (%s, %s)'''
    cursor.execute(query, (username, artistID))
    conn.commit()
    cursor.close()

    return redirect(url_for('home'))

@app.route('/unfan', methods=['GET', 'POST'])
def unfan():
    username = session['username']
    artistID = request.form['artistID']
    cursor = conn.cursor()
    query = '''delete from userfanofartist
                where username = %s and artistID = %s'''
    cursor.execute(query, (username, artistID))
    conn.commit()
    cursor.close()

    return redirect(url_for('home'))


# def allowed_file(filename):
# 	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
# @app.route('/')
# def upload_form():
# 	return render_template('upload.html')

# @app.route('/', methods=['POST'])
# def upload_file():
# 	if request.method == 'POST':
#         # check if the post request has the file part
# 		if 'file' not in request.files:
# 			flash('No file part')
# 			return redirect(request.url)
# 		file = request.files['file']
# 		if file.filename == '':
# 			flash('No file selected for uploading')
# 			return redirect(request.url)
# 		if file and allowed_file(file.filename):
# 			filename = secure_filename(file.filename)
# 			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
# 			flash('File successfully uploaded')
# 			return redirect('/')
# 		else:
# 			flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
# 			return redirect(request.url)
        
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
