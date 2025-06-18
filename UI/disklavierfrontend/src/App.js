import './App.css';
import { AppBar, Toolbar, Typography, Container } from '@mui/material';

function App() {
  return (
    <div>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Disklavier Control
          </Typography>
        </Toolbar>
      </AppBar>
      <Container>
        {/* Main content will go here */}
      </Container>
    </div>
  );
}

export default App;
