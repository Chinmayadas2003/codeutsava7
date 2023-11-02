import React, { useEffect, useState } from 'react';
import './App.css';
import { Icon, Button, Container, Grid, Typography } from '@mui/material';

function App() {

  let baseURL = 'http://172.22.130.141:5000';

  let [potData, setPotData] = useState([]);
  let [imgSrc, setImgSrc] = useState(null);

  useEffect(() => {
    fetch(baseURL + '/potholes').then(res => res.json()).then((data) => {
      data.reverse();
      console.log(data);
      setPotData(data);
    })
  }, []);

  let potList = potData.map((pot) => {
    return (
      <p>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
        <Typography>
          Pothole detected at<br></br>
          <a href={'https://www.google.com/maps/@' + pot.lat + ',' + pot.lon}>{pot.lat}, {pot.lon}</a><br/>
        </Typography>

        <Button variant="contained" onClick={() => {setImg(pot.imgName)}}>
          View
        </Button>&nbsp;
        <Button variant="contained" onClick={() => {
          setTimeout(() => {
            alert('Worker assigned, will be notified.')
          }, 1000);
        }}>
          Assign Worker
        </Button>
        <br></br>
        <Typography>
          {/* <Icon>
            pending_actions
          </Icon> */}
          {
            pot.repaired ? "Work Done" : "Repair Pending"
          }
        </Typography>
      </p>
    )
  });

  function setImg(imgName){
    setImgSrc(baseURL + '/uploads/' + imgName)
  }

  return (
    <>
      <Container>
        <Grid container spacing={3}>
          <Grid item xs={4}>
            {potList}
          </Grid>
          <Grid item xs={8}>
            <img src={imgSrc} height={640} width={640} />
          </Grid>
        </Grid>
      </Container>
    </>
  );
}

export default App;