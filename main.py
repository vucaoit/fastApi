import base64
from fastapi.responses import HTMLResponse
import os
import shutil
import uuid
from fastapi import Depends, FastAPI, Form, HTTPException, File, UploadFile, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import jwt
from datetime import datetime, timedelta
from typing import Union, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uvicorn
import crud
import models
import schemas
from security import SECRET_KEY, SECURITY_ALGORITHM, validate_token, reusable_oauth2,get_current_user
from socket import *

from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
from typing import List

app = FastAPI()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://10.250.194.207:8080/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = dict()

    async def connect(self, websocket: WebSocket,client_id:str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self,client_id:str):
        del self.active_connections[client_id]

    async def send_personal_message(self, message: str, webSocket:WebSocket):
        await webSocket.send_text(message)
   

    async def broadcast(self,target_id:str, message: str):
        for key, value in self.active_connections.items():
            if str(key) == str(target_id):
                await value.send_text(message)
        
manager = ConnectionManager()


@app.get("/")
async def get():
    return HTMLResponse(html)

@app.post("/signin/", response_model=Any)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.is_email_exist(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
@app.post("/users/email", response_model=Any)
def read_user_by_email(email: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=List[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items

# authen
def generate_token(email: Union[str, Any]) -> str:
    expire = datetime.utcnow() + timedelta(
        seconds=60 * 60 * 24 * 3  # Expired after 3 days
    )
    to_encode = {
        "exp": expire, "email": email
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=SECURITY_ALGORITHM)
    return encoded_jwt

class LoginRequest(BaseModel):
    email: str
    password: str

def verify_password(email, password,db: Session):
    user = crud.get_user(db,email)
    if (user.password == password):
        return True
    return False

@app.post('/login')
def login(request_data: LoginRequest,db : Session = Depends(get_db)):
    print(f'[x] request_data: {request_data.__dict__}')
    if verify_password(email=request_data.email, password=request_data.password,db=db):
        token = generate_token(request_data.email)
        return {
            'token': token,
            'user': crud.get_user_by_email(db,request_data.email)
        }
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.get('/books', dependencies=[Depends(validate_token)])
def list_books():
    return {'data': ['Sherlock Homes', 'Harry Potter', 'Rich Dad Poor Dad']}

@app.post("/images/")
async def create_upload_file(file: UploadFile = File(...)):

    file.filename = f"{uuid.uuid4()}.jpg"
    contents = await file.read()  # <-- Important!

    # example of how you can save the file
    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(contents)

    return {"filename": "/uploads/"+file.filename}
@app.post("/info")
def get_user_by_token(token:str,db:Session = Depends(get_db)):
    print(token)
    return get_current_user(token=token,db=db)
@app.post("/imagebase64")
def upload_image_base64(filedata: str = Form(...)):
    filename = f"{uuid.uuid4()}.jpg"
    image_as_bytes = str.encode(filedata)  # convert string to bytes
    img_recovered = base64.b64decode(image_as_bytes)  # decode base64string
    try:
        with open("uploads/" + filename, "wb") as f:
            f.write(img_recovered)
    except Exception:
        return {"message": "There was an error uploading the file"}
        
    return {"message": f"Successfuly uploaded {filename}"} 


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket,client_id)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"client #{client_id} : {data}")
            if data.__contains__('@'):
                await manager.send_personal_message(f"You wrote: {data.split('@')[1]}", websocket)
                await manager.broadcast(data.split('@')[0],f"Client #{client_id} says to #{data.split('@')[0]}: {data.split('@')[1]}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        print(f"Client #{client_id} left the chat")
#Profile API
# @app.post("/profile/", response_model=schemas.Profile)
# def create_profile(userId:int,fullName:str, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_id(db, id=userId)
#     if db_user is None:
#         raise HTTPException(status_code=402, detail="User not found")
#     return crud.create_profile(db=db, userId=userId,fullName = fullName)


#Run App
if __name__ == "__main__":
    uvicorn.run(app, host="10.250.194.207", port=8080,workers = 2, access_log=False)
    # uvicorn main:app --reload --port 8080 --host=10.250.194.207