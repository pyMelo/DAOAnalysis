# DAOAnalysis

DAOAnalysis è un progetto dedicato all'analisi delle Decentralized Autonomous Organizations (DAO) attraverso la raccolta e l'analisi di smart contract Solidity e dati correlati.

## 📌 **Indice**

- [Introduzione](#introduzione)
- [Struttura del Progetto](#struttura-del-progetto)
- [Prerequisiti](#prerequisiti)
- [Installazione](#installazione)
- [Utilizzo](#utilizzo)
- [Limitazioni e Lavori Futuri](#limitazioni-e-lavori-futuri)
- [Contribuire](#contribuire)
- [Licenza](#licenza)

---

## 🔍 **Introduzione**

Le Decentralized Autonomous Organizations (DAO) sono una componente fondamentale della finanza decentralizzata (DeFi) e della governance blockchain. Questo progetto mira a fornire strumenti per:

- Analizzare la struttura e il costo degli smart contract DAO.
- Automatizzare la raccolta e la modifica di file Solidity.
- Estrarre metriche chiave dai contratti.
- Facilitare la stima delle risorse richieste per la loro esecuzione.

Il progetto include una combinazione di script Python e JavaScript, oltre all'uso di Hardhat per la gestione e la compilazione degli smart contract.

---

## 📁 **Struttura del Progetto**

La repository è organizzata nel seguente modo:

```
DAOAnalysis/
│── contracts/             # Contiene i file Solidity degli smart contract DAO
│── dataset/               # Dataset utilizzati per l'analisi delle DAO
│── script/                # Script di automazione per la raccolta e modifica dei contratti
│── README.md              # Documentazione del progetto
│── collectFiles.py        # Script Python per raccogliere file Solidity
│── estimateBytesize.js    # Script per stimare la dimensione del bytecode degli smart contract
│── hardhat.config.js      # Configurazione di Hardhat
│── importsModifier.py     # Script Python per modificare gli import nei file Solidity
│── package.json           # Metadati del progetto Node.js
│── solidityMetrics.py     # Script Python per analizzare metriche Solidity
```

---

## ✅ **Prerequisiti**

Prima di installare il progetto, assicurati di avere i seguenti software installati sul tuo sistema:

- **[Node.js](https://nodejs.org/)** (>= v16.0.0)
- **[NPM](https://www.npmjs.com/)** o **[Yarn](https://yarnpkg.com/)**
- **[Python](https://www.python.org/)** (>= v3.8) con `pip` installato
- **[Hardhat](https://hardhat.org/)** per la gestione degli smart contract Solidity

---

## 🚀 **Installazione**

Per eseguire il progetto in locale, segui questi passaggi:

### 1️⃣ Clona la repository:

```sh
git clone https://github.com/pyMelo/DAOAnalysis.git
cd DAOAnalysis
```

### 2️⃣ Installa le dipendenze Node.js:

```sh
npm install
```

### 3️⃣ Installa le dipendenze Python:

```sh
pip install -r requirements.txt
```

*(Se non hai il file **`requirements.txt`**, potresti dover installare manualmente pacchetti come **`pandas`**, **`numpy`** o **`web3`** a seconda degli script che utilizzi.)*

---

## 🔧 **Utilizzo**

Il progetto include diversi script e configurazioni per interagire con i DAO.

### 💻 **Compilazione degli Smart Contract**

```sh
npx hardhat compile
```

### 🔥 **Esecuzione degli Script**

#### 📂 **Raccolta di file Solidity**

```sh
python script/collectFiles.py
```

#### 🔍 **Analisi delle metriche Solidity**

```sh
python script/solidityMetrics.py
```

#### 💾 **Modifica automatica degli import nei file Solidity**

```sh
python script/importsModifier.py
```

#### 📏 **Stima delle dimensioni del bytecode**

```sh
node script/estimateBytesize.js
```

---

## ⚠️ **Limitazioni e Lavori Futuri**

Nonostante il progetto abbia fornito risultati utili nell'analisi delle DAO, non è stato possibile raggiungere un'accuratezza del 100% in tutte le metriche analizzate. Alcuni aspetti, come la stima della complessità del codice e la valutazione delle transazioni on-chain, necessitano di ulteriori miglioramenti.

### 🔄 **Possibili sviluppi futuri:**

- Miglioramento dell'algoritmo di analisi delle metriche Solidity.
- Integrazione con API blockchain per ottenere dati più accurati.
- Automazione della verifica degli smart contract direttamente sulla blockchain.
- Supporto a un numero maggiore di DAO e protocolli DeFi.

Questi aspetti verranno approfonditi nelle versioni future del progetto.

---

## 🤝 **Contribuire**

Se vuoi contribuire:

1. **Forka** la repository.
2. **Clona** la tua copia in locale:
   ```sh
   git clone https://github.com/tuo-username/DAOAnalysis.git
   ```
3. **Crea un nuovo branch** per le modifiche:
   ```sh
   git checkout -b my-feature-branch
   ```
4. **Apporta le modifiche e fai un commit**:
   ```sh
   git add .
   git commit -m "Aggiunta di una nuova funzionalità"
   ```
5. **Pusha il branch** e invia una **pull request**:
   ```sh
   git push origin my-feature-branch
   ```

---

## 📜 **Licenza**

Questo progetto è rilasciato sotto licenza **MIT**. Per maggiori dettagli, consulta il file [LICENSE](LICENSE).

---


🔹 **DAOAnalysis** è un progetto in continua evoluzione. Se hai suggerimenti o vuoi contribuire, sentiti libero di farlo! Grazie per il supporto. 🚀✨
