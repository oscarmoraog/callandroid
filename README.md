# CallAndroid

Ponte entre links no Notion e o discador do Android via ADB.

```
Notion link → localhost:39527 → ADB → Android liga
```

## Como funciona

1. Clique num link no Notion
2. Abre uma aba no browser com o status da chamada
3. O Android disca automaticamente via ADB
4. Quando desligar no phone, a aba atualiza em tempo real (SSE)

## Requisitos

- Windows 10 ou 11
- Android com depuração USB ativada
- ADB (Android SDK Platform Tools)

## Instalar ADB

1. Baixe [Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools)
2. Extraia para `C:\platform-tools`
3. Adicione `C:\platform-tools` ao PATH do Windows
4. Teste: `adb devices`

## Configurar o Android

1. **Configurações** → **Sobre o telefone** → toque 7x em **Número da versão**
2. Abra **Opções do desenvolvedor** → ative **Depuração USB**
3. Conecte via USB e aceite **"Permitir depuração USB?"**
4. Teste: `adb devices` deve mostrar `XXXXXXXX    device`

## Instalar

1. Clique com botão direito em `install.bat`
2. Selecione **"Executar como administrador"**
3. Pronto! O executável é gerado e o servidor inicia automaticamente

O `install.bat`:
- Verifica Python e PyInstaller
- Gera `dist\CallAndroid.exe`
- Registra auto-start no Windows (via VBS)
- Cria atalho no Desktop

## Usar no Notion

URL do link:

```
http://localhost:39527/call/5511999999999?nome=Lumikit&contato=(11)999999999
```

Parâmetros:
- **Telefone** (obrigatório): número com código do país
- **nome** (opcional): exibe o nome do cliente na página
- **contato** (opcional): exibe informações adicionais de contato

### Exemplo na tabela do Notion

| Nome   | Telefone          | Link de ligação |
| ------ | ----------------- | --------------- |
| Lumikit | +55 11 94832-3837 | [Ligar](http://localhost:39527/call/5511948323837?nome=Lumikit&contato=(11)999999999) |

## Endpoints

| Rota | Método | Descrição |
| ---- | ------ | --------- |
| `/` | GET | Página principal (idle ou chamada em andamento) |
| `/call/<telefone>` | GET | Inicia a ligação |
| `/hangup` | GET | Desliga a chamada |
| `/ended` | GET | Página "Chamada encerrada" |
| `/status` | GET | Status atual: `calling`, `idle` ou `error:<msg>` |
| `/events` | GET | SSE em tempo real (push de status) |

## Testar

```bat
cd tests
python -m pytest test_phone.py test_adb.py -v
```

## Troubleshooting

### "ADB não encontrado"
Instale o Android SDK Platform Tools e adicione ao PATH.

### "Nenhum dispositivo Android conectado"
Conecte o Android via USB com depuração USB ativada.

### "O Android ainda não autorizou este computador"
Verifique a tela do celular e aceite a autorização.

### Ligação não aparece no phone
Verifique se o ADB está funcionando: `adb devices` deve mostrar `device`.
