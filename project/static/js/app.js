const ws = new WebSocket("ws://127.0.0.1:8001/ws");

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    const table = document.getElementById("signals");
    table.innerHTML = "";

    data.forEach(item => {
        let row = `<tr>
            <td>${item.symbol}</td>
            <td class="${item.signal.includes('Buy') ? 'buy' : item.signal.includes('Sell') ? 'sell' : 'neutral'}">
                ${item.signal}
            </td>
            <td>${item.price}</td>
            <td>${item.confidence}%</td>
            <td>${item.sl}</td>
            <td>${item.tp}</td>
        </tr>`;

        table.innerHTML += row;
    });
};