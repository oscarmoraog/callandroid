# CallAndroid

Ponte simples entre links no Notion e o discador do Android via ADB.

```
Notion → callandroid:// → CallAndroid.exe → ADB → Android abre discador
```

## Requisitos

- Windows 10 ou 11
- Android com depuração USB ativada
- ADB (Android SDK Platform Tools)

## Instalar ADB

1. Baixe [Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools)
2. Extraia para `C:\platform-tools`
3. Adicione `C:\platform-tools` ao PATH do Windows
4. Teste: abra o CMD e execute `adb devices`

## Configurar o Android

1. Abra **Configurações** → **Sobre o telefone**
2. Toque 7 vezes em **Número da versão** (ativa Modo Desenvolvedor)
3. Volte e abra **Opções do desenvolvedor**
4. Ative **Depuração USB**
5. Conecte o Android via cabo USB
6. Aceite a mensagem **"Permitir depuração USB?"** no celular
7. Teste: `adb devices` deve mostrar `XXXXXXXX    device`

## Instalar CallAndroid

1. Clique com o botão direito em `install.bat`
2. Selecione **"Executar como administrador"**
3. Pronto! O executável é gerado e o protocolo `callandroid://` é registrado automaticamente

## Como usar no Notion

1. Crie um campo **Telefone** com o número no formato `+5511999999999`
2. Crie um link com URL: `callandroid://5511999999999`
3. Clique no link → o Android abre o discador com o número

### Exemplo na tabela do Notion

| Nome   | Telefone           | Ligar      |
| ------ | ------------------ | ---------- |
| João   | +55 11 99999-9999  | 📞 Ligar  |
| Maria  | +55 11 98888-8888  | 📞 Ligar  |

O link de "📞 Ligar" deve apontar para `callandroid://5511999999999`.

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

### "O dispositivo Android está offline"
Reconecte o cabo USB e tente novamente.
