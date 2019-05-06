from flask import Flask, session, render_template, request, escape
from flask import copy_current_request_context
from vsearch import search4letters
from DBcm import UseDatabsase, ConnectionError, CredentialsError, SQLError
from checker import check_logged_in
from threading import Thread

def search4letters(pharse:str, letters:str='aeiou')->set:
    """Returns the set of 'letters' that found in 'pharse'."""
    return set(pharse).intersection(set(letters))
app = Flask(__name__)

app.secret_key = 'YouWillNeverGuss'

app.config['dbconfig'] = {
                        'host': '127.0.0.1',
                        'user': 'root',
                        'password': 'sabeer',
                        'database': 'vsearchlogdb',
                        }


@app.route('/')
@app.route('/entry')
def entry() -> 'html':
    return render_template('entry.html', the_title="Enter fields to get search results!")


@app.route('/search4', methods=['POST'])
def do_search() -> 'html':

    @copy_current_request_context
    def log_request(req: 'flask_request', res: str) -> None:
        """ log the details of web request and results."""
        try:
            with UseDatabsase(app.config['dbconfig']) as cursor:
                sql = """INSERT INTO log(phrase, ip, browser_string, results, letters) 
                        VALUES(%s, %s, %s, %s, %s)"""
                cursor.execute(sql, (req.form['phrase'],
                                     req.remote_addr,
                                     req.user_agent.browser,
                                     res,
                                     req.form['letters'],
                                     ))
        except ConnectionError as err:
                print('Is your database is switch on ? Error: ', str(err))
        except CredentialsError as err:
                print('user-id/password Error: ', str(err))
        except SQLError as err:
                print('Is your query correct ? Error: ', str(err))
        except Exception as err:
                print('something went wrong! Error: ', str(err))
    phrase = request.form["phrase"]
    letters = request.form["letters"]
    result = str(search4letters(phrase, letters))
    try:
        # log_request(request, result)
        t = Thread(target=log_request, args=(request, result))
        t.start()
    except Exception as exe:
            print("Logging in failed due to the following Error: ", str(exe))    
    return render_template('results.html',
                           the_title="Here are your results!",
                           the_phrase=phrase,
                           the_letters=letters,
                           the_result=result, )    

@app.route('/login')
def logIn() ->str:
    session['logging_in'] = True
    return "you are logged in."


@app.route('/viewlog')
@check_logged_in
def view_the_log() -> 'html':
    try:
        with UseDatabsase(app.config['dbconfig']) as cursor:
            sql = """SELECT phrase, letters, ip, browser_string, results FROM log """
            cursor.execute(sql)
            contents = cursor.fetchall()
        titles = ['Input', 'letters', 'Remote_Addr', 'User_Agent', 'Result']
        return render_template('viewlog.html',
                               the_title='viewlog',
                               row_titles=titles,
                               the_data=contents, )
    except ConnectionError as err:
            print('Is your database is switch on ? Error: ', str(err))
    except CredentialsError as err:
            print('user-id/password Error: ', str(err))
    except SQLError as err:
            print('Is your query correct ? Error: ', str(err))
    except Exception as err:
            print('something went wrong! Error: ', str(err))
  


@app.route('/logout')
def logOut() -> str:
    session.pop('logging_in')
    return 'you are logged out'

if __name__ == '__main__':
    app.run(debug=True)
