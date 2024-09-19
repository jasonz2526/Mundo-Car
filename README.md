# Mundo Car

## Description

**Mundo Car** is a personal project designed to provide detailed insights into League of Legends gameplay. By utilizing a React frontend and Flask backend with MongoDB, Mundo Car allows users to compare their in-game performance against high elo players, offering strategic feedback to help them improve.

### Key Features:
- **RESTful APIs**: Built using Flask to handle requests and serve data efficiently.
- **MongoDB Integration**: Scalable storage solution for player statistics, match histories, and game-related data.
- **Asynchronous Data Fetching**: Axios in React is used to fetch and display historical player data.
- **Interactive Visualizations**: Created with Chart.js, these visualizations allow users to compare their stats with high-level players, enhancing the analysis with dynamic CSS styling.

## Checklist of Things to Accomplish

1. **Make MongoDB Cloud-Based**:  
   Replace the local MongoDB instance with a cloud-hosted solution like MongoDB Atlas. This will allow the app to run on any device, enabling seamless access to the database from anywhere.

2. **AI/ML Integration for Pattern Recognition**:  
   Incorporate machine learning models to better predict patterns in player performance, such as identifying trends in farming, ganking, and objective control compared to high-level players. This will enable more personalized feedback and strategic recommendations for users.

3. **Real-Time Data Processing**:  
   Implement real-time data fetching and processing to give users immediate feedback on their gameplay during live matches. This would enhance the functionality of the app beyond post-game analysis.

4. **Add Advanced Visualization Features**:  
   Expand the current Chart.js implementation to include more interactive and insightful visualizations. Potential features include a heat map for jungle positioning, timelines of game events, and side-by-side comparisons of user and pro-player actions.

5. **Cross-Platform Compatibility**:  
   Ensure that the app is compatible across multiple platforms (e.g., desktop, tablet, mobile). This requires optimizing the UI/UX design and adding responsive elements to the React frontend.

6. **Enhance User Authentication and Profiles**:  
   Add user authentication (e.g., OAuth, JWT) and profile management so users can save their match history, performance data, and tracked improvements over time.

7. **Introduce More Roles**:  
   Create more interactive graphs pertaining to specific roles of League, as right now only Jungle has been fully fleshed out.

## Demonstration

To see Mundo Car in action, check out the demonstration below:

### GIFs & Images
- **Overview of Player Stats Comparison**:
![WIP]()

- **Interactive Charts**:
![WIP]()

### Video
- **Project Demo**:
[![WIP]()]()

## Acknowledgments

- **Flask**: For the robust backend API framework.
- **MongoDB**: For scalable data storage.
- **React**: For a dynamic and responsive frontend.
- **Chart.js**: For creating interactive data visualizations.
- **Axios**: For handling asynchronous HTTP requests.
