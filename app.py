from flask import Flask, render_template, request
import re

app = Flask(__name__)

class KnightsKnavesSolver:
    def __init__(self):
        self.truth_table = {
            'A': None,
            'B': None
        }
    
    def evaluate_statement(self, statement, assignments):
        # Replace variables with their truth values
        expr = statement
        expr = expr.replace('p', str(assignments.get('A', False)))
        expr = expr.replace('q', str(assignments.get('B', False)))
        
        # Replace logical operators
        expr = expr.replace('¬', ' not ')
        expr = expr.replace('∧', ' and ')
        expr = expr.replace('∨', ' or ')
        expr = expr.replace('→', ' <= ')  # p → q is equivalent to ¬p ∨ q, which is not p or q
        expr = expr.replace('↔', ' == ')  # p ↔ q is p == q
        
        try:
            expr = re.sub(r'(\w+|\([^)]+\))\s*<=\s*(\w+|\([^)]+\))', r'(not \1) or \2', expr)
            return eval(expr)
        except:
            return False
        
    def generate_truth_table(self, statement, speaker, identity_a, identity_b):
        """Generate complete truth table showing all possible combinations"""
        truth_table = []
        consistent_solutions = []
        
        # Try all possible assignments for A and B
        for a_is_knight in [True, False]:
            for b_is_knight in [True, False]:
                assignments = {'A': a_is_knight, 'B': b_is_knight}
                
                # p is true if A's actual identity matches the user-defined proposition
                p_value = (a_is_knight and identity_a == 'knight') or (not a_is_knight and identity_a == 'knave')
                # q is true if B's actual identity matches the user-defined proposition  
                q_value = (b_is_knight and identity_b == 'knight') or (not b_is_knight and identity_b == 'knave')
                
                # Update assignments for statement evaluation
                statement_assignments = {'A': p_value, 'B': q_value}
                
                # Evaluate the statement using proposition truth values
                try:
                    statement_value = self.evaluate_statement(statement, statement_assignments)
                except:
                    statement_value = False
                
                # Determine if speaker tells the truth
                speaker_is_knight = assignments[speaker]
                
                # Check consistency: Knights tell truth, Knaves lie
                consistent = (speaker_is_knight and statement_value) or (not speaker_is_knight and not statement_value)
                
                row = {
                    'a_identity': 'Knight' if a_is_knight else 'Knave',
                    'b_identity': 'Knight' if b_is_knight else 'Knave',
                    'p_value': p_value,
                    'q_value': q_value,
                    'statement_value': statement_value,
                    'speaker_truth': speaker_is_knight,
                    'consistent': consistent
                }
                
                truth_table.append(row)
                
                if consistent:
                    consistent_solutions.append({
                        'a_identity': 'Knight' if a_is_knight else 'Knave',
                        'b_identity': 'Knight' if b_is_knight else 'Knave'
                    })
        
        return truth_table, consistent_solutions

    def solve_puzzle(self, statements):
        results = []
        
        # Try all possible assignments for A and B
        for a_is_knight in [True, False]:
            for b_is_knight in [True, False]:
                assignments = {'A': a_is_knight, 'B': b_is_knight}
                is_consistent = True
                
                for stmt in statements:
                    speaker = stmt['speaker']
                    statement = stmt['statement']
                    
                    # Evaluate the statement
                    statement_value = self.evaluate_statement(statement, assignments)
                    
                    # Check consistency: Knights tell truth, Knaves lie
                    speaker_is_knight = assignments[speaker]
                    
                    if speaker_is_knight and not statement_value:
                        # Knight said something false
                        is_consistent = False
                        break
                    elif not speaker_is_knight and statement_value:
                        # Knave said something true
                        is_consistent = False
                        break
                
                if is_consistent:
                    return {
                        'consistent': True,
                        'solution': {
                            'A': 'Knight' if a_is_knight else 'Knave',
                            'B': 'Knight' if b_is_knight else 'Knave'
                        }
                    }
        
        return {'consistent': False, 'solution': None}

@app.route('/', methods=['GET', 'POST'])
def solve():
    if request.method == 'GET':
        return render_template('index.html')

    speaker = request.form.get('speaker')
    statement = request.form.get('statement', '').strip()
    identity_a = request.form.get('identity_a', 'knight')
    identity_b = request.form.get('identity_b', 'knave')

    if not speaker or not statement:
        return render_template('index.html', 
                             error="Please select a speaker and enter a statement.",
                             speaker=speaker, 
                             statement=statement)
    
    solver = KnightsKnavesSolver()
    
    try:
        truth_table, consistent_solutions = solver.generate_truth_table(statement, speaker, identity_a, identity_b)
        
        return render_template('index.html',
                             truth_table=truth_table,
                             consistent_solutions=consistent_solutions,
                             speaker=speaker,
                             statement=statement,
                             identity_a=identity_a,
                             identity_b=identity_b)
    
    except Exception as e:
        return render_template('index.html', 
                             error=f"Error processing statement: {str(e)}",
                             speaker=speaker, 
                             statement=statement)

if __name__ == '__main__':
    app.run(debug=True)
