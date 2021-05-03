# Pizza Time
[See the Demo on Heroku!](https://sams-pizza-time.herokuapp.com/demo/login)

This app works by getting current delivery data from the specified API, and presenting it simply for easy consumption during the delivery. 

These deliveries are stored (along with thier tip information) so you can review your stats.

If your chosen API has schedule information, This is also pulled and stored, so more metrics, such has Tips/Hour can be given

I implemented a peer created notes system for customers so drivers can help other drivers have easier deliveries. I chose to Implement this feature becuase I had always thought it would be useful, but have never seen it. 

You enter the site through /<api>/login. Once logged in, you are dropped on the /current_delivery page. 


![Example Of /current_delivery page](https://i.ibb.co/QXR4cVS/curr-dels.png)

#### On the /current_delivery page,
 If you have a delivery, All orders on the delivery are displayed. Each order displays all relevant information - customer address, customer name, customer phone number, order tip, A link to google maps navigation to the orders address, and a link to dial the customers number.

Otherwise, you can use the Nav bar at the top of the screen to go to either dashboard, edit_deliveries, show_schedule, or logout.

![Example Of /edit_deliveries page](https://i.ibb.co/71v1sMy/edit-delivery.png)

#### On the /edit_deliveries page, 
 a driver can edit tips on all previous deliveries stored in the DB.

![Example Of /schedule page](https://i.ibb.co/mz6V8DH/Screenshot-at-2021-05-02-19-19-12.png)

####On the /show_schedules page,
 The schedule for the current user is displayed.

![Example Of /dashboard page](https://i.ibb.co/NCpL58c/dashboard.png)

#### On the /Dashboard page,
 a driver can view their stats



#### This API is set up to work out of the box with 2 API's
- Demo Api (Internally Created)
- Pag Api [Link](https://www.sam-the-dev.com/)*

 *You must be an employee of Pagliacci Pizza to use the Pag Api


#### Programs This Project Uses
- Python as the server language
- Gunicorn as a WSGI
- Flask as a Web Framework
- Postgresql as a DB
- SQLAlchemy as an ORM

#### To get this site up and running on a local linux server, you will need to have postgresql installed.
Simply follow these steps
1. Clone the repo,  
2. Create a venv (and source it),  
3. Install the dependencies listed in requirements.txt,  
4. Create a DB in postgres called 'pizza-time' (and 'pizza-time-test' to run the test files),  
5. Run the app.py with 'flask run' and everything should start rolling!

