const net = require('net'); //node.jsのビルトインモジュールnetを使用してunixソケットにつなぐ

//標準入力からサーバへのリクエスト情報を取得する
const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

async function getUserInput(question) {
    return new Promise((resolve) => {
        rl.question(question, (userInput) => {
            resolve(userInput);
        });
    });
}


async function main() {
    const SERVER_ADDRESS = '/tmp/rpc.sock';
    // const one_arg_methods = ['floor', 'reverse', 'sort']
    const two_arg_methods = ['nroot', 'valid_anaglam']

    const method = await getUserInput('input method: ');
    const params = [];
        
    //メソッドに応じてユーザーに求める引数の数を変更する
    if (two_arg_methods.includes(method)){
        arg_num = 2
        for (let i = 0; i < arg_num; i++){
            params[i] = await getUserInput(`input params${i + 1}: `);
        }
    } else {
        params[0] = await getUserInput('input param: ');
    }

    //入力された引数の型を取得する(今回は数値の文字列は扱わないことにする)
    const param_types = params.map(param => {
        const value = parseFloat(param);
        if (isNaN(value)){
            return typeof param;
        } else {
            return typeof value;
        }
    })

    const id = await getUserInput('input your id: ');

    //入力されたデータをJSON形式にまとめる
    const jasonData = {
        "method": method,
        "params": params,
        "param_types": param_types,
        "id": id
    };

    //通信を開始
    const client = new net.Socket();
    client.connect(SERVER_ADDRESS, function() {
        console.log('Connected to server')
        
        const jsonString = JSON.stringify(jasonData)
        console.log(`request: ${jsonString}`)
        const jsonDataBuffer = Buffer.from(jsonString, 'utf-8');
        client.write(jsonDataBuffer);
    });

    //サーバの応答を受ける
    client.on("data", data => {
        receivedJson = JSON.parse(data)
        console.log(receivedJson);
        client.end()
    })
    client.on('error', function(err) {
        console.error('Connection failed:', err.message);
    });

    client.on('close', function() {
        console.log('Connection closed');
    });
}


main();



