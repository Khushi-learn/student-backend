from fastapi import FastAPI,HTTPException
import psycopg2
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
load_dotenv()
app =FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["GET","POST"],
    allow_headers=["AUTHORIZATION"],
)


Connection =psycopg2.connect(os.getenv('DATABASE_URL')
)
cursor =Connection.cursor()
class Student(BaseModel):
    id:int =None
    name:str =None
    course:str =None

@app.get('/students')
def get_all_students():
    cursor.execute('SELECT* FROM students')
    rows =cursor.fetchall()
    # print(rows) #[(101, 'Steve Jobs', 'AI')]
    #[{'id':101,}]
    result =[]
    for row in rows:
        result.append({
            'id':row[0],
            'name':row[1],
            'course':row[2]
        })

    return result

@app.get('/students/{id}')
def get_single_students(id:int):
    try:
        cursor.execute('SELECT *FROM students WHERE id =%s',(id,) )
        row =cursor.fetchone()
        return{
            'id':row[0],
            'name' :row[1],
            'course' :row[2]
        }
    except Exception as e:
        raise HTTPException(status_code=404,detail='student record not found')

        

#create student record
@app.post('/students')
def create_students_record(student:Student):
    try:
        cursor.execute('INSERT INTO students VALUES(%s,%s,%s)',(student.id,student.name,student.course))
        Connection.commit()
        return{
            'message':'student Record Created Successfully'
        }
    except psycopg2.IntegrityError:
        Connection.rollback()
        raise HTTPException(status_code=404,detail='student record already exist')

    
#replace student record
@app.put('/students/{id}')
def replace_student_record(id:int,student:Student):
    try:
        cursor.execute('UPDATE students SET id =%s,name =%s,course=%s WHERE id=%s',(student.id,student.name,student.course,id))
        Connection.commit()
        if(cursor.rowcount == 0):
            raise HTTPException(status_code=404,detail='student id not found')
        else:

            return {
            'message':'student record successfully updated'
            }
    except Exception as e:
        raise HTTPException(status_code=404,detail=f'str({e})')

        

        
#partilly update student record 
@app.patch('/students/{id}')
def partially_update_student_record(id:int,student:Student):
    if(student.id !=None):
        cursor.execute('UPDATE students SET id =%s WHERE id =%s',(student.id,id))
        Connection.commit()
    return{
        'message':'student record is partially updated'
    }

@app.delete('/students/{id}')
def remove_student_record(id:int):
    cursor.execute('DELETE FROM students WHERE id =%s',(id,))
    Connection.commit()
    if(cursor.rowcount ==0):
        raise HTTPException(status_code=404,detail='student id not found')
    else:
   
        return {
        'message':'successfully remove student record'
        }


