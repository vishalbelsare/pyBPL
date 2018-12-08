import numpy as np

class Dataset(object):
    def __init__(self,drawings,images,names,timing):
        
        '''
        USAGE:
        import numpy as np
        from scipy.io import loadmat
        data = loadmat('data_background',variable_names=['drawings','images','names','timing'])
        D = Dataset(data['drawings'],data['images'],data['names'],data['timing'])
        
        Images are 105x105 are retrieved with:
        D.images[alphabet][character][rendition] 

        Drawings of a particular image are lists of strokes, where each
        stroke is a list of timesteps, where each timestep is an (x,y) coord.
        (x,y) coords of drawings are retrieved with:
        D.drawings[alphabet][character][rendition][stroke][timestep]
        
        NOTES: 
        (1) ONLY CLEANING UP DRAWINGS AND IMAGES FOR NOW.
            NAMES AND TIMING HAVE UNSPECIFIED INDEX STURCTURE FOR NOW, NOT SAVING THEM IN CLASS
        
        (2) ASK BRENDEN ABOUT FLIP_IMG
        '''

        self.names = names

        im_0 = images[0][0][0][0][0][0]
        assert im_0.shape==(105,105)
        self.flip_img = not self.check_black_is_true(im_0)
        
            
        self.images = {}
        self.drawings = {}
        
        n_alpha = len(images)
        for a in range(n_alpha):
            
            alphabet = images[a][0]
            n_char = len(alphabet)
            
            self.images[a] = {}
            self.drawings[a] = {}
            
            for c in range(n_char):
                
                character = alphabet[c][0]
                n_rend = len(character)
                
                self.images[a][c] = {}
                self.drawings[a][c] = {}
                
                for r in range(n_rend):
                    
                    rendition_image = character[r][0]
                    rendition_drawing = drawings[a][0][c][0][r][0]
                    num_strokes = len(rendition_drawing)
                    
                    self.images[a][c][r] = rendition_image
                    
                    # NOTE: ASK BRENDEN ABOUT THIS
                    if self.flip_img:
                        self.images[a][c][r] = (1 - self.images[a][c][r])
                    
    
                    self.drawings[a][c][r] = {}
                    
                    for s in range(num_strokes):
                        
                        stroke = rendition_drawing[s][0]
                        discrete_steps = len(stroke)
                        times = timing[a][0][c][0][r][0][s][0][0]
                        
                        self.drawings[a][c][r][s] = np.zeros((discrete_steps,3))
                
                        for discrete_step in range(discrete_steps):
                            assert len(stroke)==len(times)
                            x,y = stroke[discrete_step]
                            t = times[discrete_step]
                            self.drawings[a][c][r][s][discrete_step] = [x,y,t]
                            
     
    def check_black_is_true(self,I):
        '''
        NOTE: ASK BRENDEN ABOUT THIS
        
        Check whether the black pixels are labeled as
        "true" in the image format, since there should be fewer
        black pixels
        '''
        return ((I==True).sum() < (I==False).sum())

    def first_stroke_locations(self):
        
        first_strokes = []

        n_alpha = len(self.drawings)
        for a in range(n_alpha):
            alphabet = self.drawings[a]
            n_char = len(alphabet)
            for c in range(n_char):
                char = alphabet[c]
                n_rend = len(char)
                for r in range(n_rend):
                    rendition = char[r]
                    stroke=0
                    first_stroke = rendition[stroke]
                    discrete_step = 0
                    x,y,t = first_stroke[discrete_step]
                    first_stroke_start = [x,y]
                    first_strokes.append(first_stroke_start)

        first_strokes = np.vstack(first_strokes)
        return first_strokes
