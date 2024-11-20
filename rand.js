const response = await fetch(
    "https://api.syndicate.io/transact/sendTransaction",
      {
        method: "POST",
        headers: {
          Authorization: "Bearer vwZ0Hz1i0FKWwyInNy0B",
          "Content-type": "application/json"
        },
        body: JSON.stringify({
          projectId: "f31d450f-b38f-4494-b64a-7f3aa2c73499",
          contractAddress: "0x52962dd492dDDef76d4eFb2bB7E505aeAE4554A1",
          chainId: 11155111,
          functionSignature: "mint(address account)",
          args: {
            account: "0xCd6b8d53C69f04be5999319CaBfC0E8EE759a20A"
          }
        })
      }
    )
