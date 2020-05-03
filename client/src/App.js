import React from 'react';
import './App.css';

class App extends React.Component {

  constructor(props) {
    super(props)
    this.state = {
      data: []
    };

    this.handleClick = this.handleClick.bind(this);

  }

  handleClick(e) {
    e.preventDefault();
    console.log('The link was clicked.');
    fetch('http://localhost:5000/api/join_game', {
      mode: "no-cors",
      method: "POST",
      body: {'player': 'alana'}
    })
    .then(res => console.log(res))
  }

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <button onClick={this.handleClick}>
          Join Game
          </button>
        </header>
      </div>
    );
  
  }
}

export default App;
