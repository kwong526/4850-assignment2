import React, {useEffect, useState} from "react";
import "../App.css";

export default function HealthCheck() {
  const [isLoaded, setIsLoaded] = useState(false);
  const [health, setStats] = useState({});
  const [error, setError] = useState(null);

  const getHealth = () => {
    fetch(`http://acit3855-kafkalab.westus3.cloudapp.azure.com:8120/health`)
      .then(res => res.json())
      .then(
        result => {
          console.log("Received Health Points");
          setStats(result);
          setIsLoaded(true);
        },
        error => {
          setError(error);
          setIsLoaded(true);
        }
      )
  };
  useEffect(() => {
    const interval = setInterval(() => getHealth(), 20000); // Update every 2 seconds
    return () => clearInterval(interval);
  }, [getHealth]);

  if (error) {
    return <div className={"error"}>Error found when fetching from API</div>;
  } else if (isLoaded === false) {
    return <div>Loading...</div>;
  } else if (isLoaded === true) {
    return (
      <div>
        <h1>Health Points</h1>
        <table className={"StatsTable"}>
          <tbody>
            <tr>
              <th> Receiver: {health["receiver"]}</th>
            </tr>
            <tr>
              <th> Storage: {health["storage"]}</th>
            </tr>
            <tr>
              <th> Processing: {health["processing"]}</th>
            </tr>
            <tr>
              <th> Audit: {health["audit"]}</th>
            </tr>
            <tr>
              <th>Last Updated: {health["last_updated"]} </th>
            </tr>
          </tbody>
        </table>
      </div>
    );
  }
}
