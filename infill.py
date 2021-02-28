# Imports
import os.path
import pickle
import ilm.tokenize_util
from transformers import GPT2LMHeadModel
from ilm.infer import infill_with_ilm

# Variables
MODEL_DIR = 'models'
MASK_CLS = 'ilm.mask.hierarchical.MaskHierarchical'
result = []
tokenizer = ilm.tokenize_util.Tokenizer.GPT2

datamodel = 'models/pytorch_model.bin'



# Create context
context = 'The sun is shining. _ All the children want to swim.'


class INFILL:
    def __init__(self):
        super().__init__()
        device = 'cpu'
        self.model = GPT2LMHeadModel.from_pretrained(MODEL_DIR)
        self.model.eval()
        self.model.to(device)
        with open(os.path.join(MODEL_DIR, 'additional_ids_to_tokens.pkl'), 'rb') as f:
            self.additional_ids_to_tokens = pickle.load(f)
        self.additional_tokens_to_ids = {v: k for k, v in self.additional_ids_to_tokens.items()}
        print('additional_ids_to_tokens', self.additional_ids_to_tokens)
        try:
            ilm.tokenize_util.update_tokenizer(self.additional_ids_to_tokens, tokenizer)
        except ValueError:
            print('Already updated')



    def infilling_word(self, context: str, order: int, mask:str):
        result.clear()
        # with open(os.path.join(MODEL_DIR, 'additional_ids_to_tokens.pkl'), 'rb') as f:
        #     additional_ids_to_tokens = pickle.load(f)
        # additional_tokens_to_ids = {v: k for k, v in additional_ids_to_tokens.items()}
        # try:
        #     ilm.tokenize_util.update_tokenizer(additional_ids_to_tokens, tokenizer)
        # except ValueError:
        #     print('Already updated')

        # Load model
        # device = 'cpu'
        # model = GPT2LMHeadModel.from_pretrained(MODEL_DIR)
        # model.eval()
        # _ = model.to(device)


        context_ids = ilm.tokenize_util.encode(context, tokenizer)
        _blank_id = ilm.tokenize_util.encode(' _', tokenizer)[0]
        print('blank', _blank_id)
        print('context', context)
        # Infilling type: One of sentence, document, mixture, paragraph, ngram, or word
        # context_ids[context_ids.index(_blank_id)] = additional_tokens_to_ids['<|infill_word|>']
        print('before', context_ids)
        count_mask = 0
        for i in range(len(context_ids)):
            if _blank_id == context_ids[i]:
                if mask[count_mask] == 'word':
                    context_ids[i] = self.additional_tokens_to_ids['<|infill_word|>']
                if mask[count_mask] == 'sent':
                    context_ids[i] = self.additional_tokens_to_ids['<|infill_sentence|>']
                count_mask+=1
        print('after', context_ids)

        generated = infill_with_ilm(
            self.model,
            self.additional_tokens_to_ids,
            context_ids,
            num_infills=order)
        for g in generated:
            result.append(str(ilm.tokenize_util.decode(g, tokenizer)))
        return result
