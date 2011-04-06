/****************************************************************/
/*               DO NOT MODIFY THIS HEADER                      */
/* MOOSE - Multiphysics Object Oriented Simulation Environment  */
/*                                                              */
/*           (c) 2010 Battelle Energy Alliance, LLC             */
/*                   ALL RIGHTS RESERVED                        */
/*                                                              */
/*          Prepared by Battelle Energy Alliance, LLC           */
/*            Under Contract No. DE-AC07-05ID14517              */
/*            With the U. S. Department of Energy               */
/*                                                              */
/*            See COPYRIGHT for full restrictions               */
/****************************************************************/

#ifndef NONLINEARSYSTEM_H
#define NONLINEARSYSTEM_H

#include "SystemBase.h"
#include "KernelWarehouse.h"
#include "BCWarehouse.h"
#include "StabilizerWarehouse.h"
#include "DiracKernelWarehouse.h"
#include "DamperWarehouse.h"

#include "transient_system.h"
#include "nonlinear_implicit_system.h"
#include "numeric_vector.h"
#include "sparse_matrix.h"
#include "preconditioner.h"

class MProblem;

/**
 * Nonlinear system to be solved
 *
 * It is a part of MProblem ;-)
 */
class NonlinearSystem : public SystemTempl<TransientNonlinearImplicitSystem>
{
public:
  NonlinearSystem(MProblem & problem, const std::string & name);
  virtual ~NonlinearSystem();

  virtual void init();

  // Setup Functions ////
  virtual void initialSetupBCs();
  virtual void initialSetupKernels();
  virtual void timestepSetup();
  
  virtual bool converged();

  void addKernel(const std::string & kernel_name, const std::string & name, InputParameters parameters);
  void addBoundaryCondition(const std::string & bc_name, const std::string & name, InputParameters parameters);
  void addDiracKernel(const std::string & kernel_name, const std::string & name, InputParameters parameters);
  void addStabilizer(const std::string & stabilizer_name, const std::string & name, InputParameters parameters);
  void addDamper(const std::string & damper_name, const std::string & name, InputParameters parameters);

  /// Adds a vector to the system
  void addVector(const std::string & vector_name, const bool project, const ParallelType type, bool zero_for_residual);

  void computeResidual(NumericVector<Number> & residual);
  void computeJacobian(SparseMatrix<Number> &  jacobian);
  void computeJacobianBlock(SparseMatrix<Number> & jacobian, libMesh::System & precond_system, unsigned int ivar, unsigned int jvar);
  Real computeDamping(const NumericVector<Number>& update);

  void printVarNorms();

  void timeSteppingScheme(Moose::TimeSteppingScheme scheme);
  /**
   * Get the order of used time integration scheme
   */
  Real getTimeSteppingOrder() { return _time_stepping_order; }

  void onTimestepBegin();

  virtual void subdomainSetup(unsigned int subdomain, THREAD_ID tid);

  virtual void set_solution(const NumericVector<Number> & soln);

  virtual NumericVector<Number> & solutionUDot() { return _solution_u_dot; }
  virtual NumericVector<Number> & solutionDuDotDu() { return _solution_du_dot_du; }

  virtual const NumericVector<Number> * & currentSolution() { return _current_solution; }

  virtual void serializeSolution();
  virtual NumericVector<Number> & serializedSolution();
      
  virtual NumericVector<Number> & residualCopy();

  void augmentSendList(std::vector<unsigned int> & send_list);

  void setPreconditioner(Preconditioner<Real> *pc);

  void setupDampers();
  void reinitDampers(THREAD_ID tid);

  /// System Integrity Checks
  void checkKernelCoverage(const std::set<subdomain_id_type> & mesh_subdomains) const;
  void checkBCCoverage(const std::set<short> & mesh_bcs) const;
  bool containsTimeKernel();

public:
  MProblem & _mproblem;
  // FIXME: make these protected and create getters/setters
  Real _last_rnorm;
  Real _l_abs_step_tol;
  Real _initial_residual;

protected:
  void computeTimeDeriv();
  void computeResidualInternal(NumericVector<Number> & residual);
  void finishResidual(NumericVector<Number> & residual);

  void computeDiracContributions(NumericVector<Number> * residual, SparseMatrix<Number> * jacobian = NULL);

  const NumericVector<Number> * _current_solution;      /// solution vector from nonlinear solver
  NumericVector<Number> & _solution_u_dot;              /// solution vector for u^dot
  NumericVector<Number> & _solution_du_dot_du;          /// solution vector for {du^dot}\over{du}
  NumericVector<Number> & _residual_old;                /// residual evaluated at the old time step (need for Crank-Nicolson)

  NumericVector<Number> & _serialized_solution;         /// Serialized version of the solution vector

  NumericVector<Number> & _residual_copy;               /// Copy of the residual vector

  Real & _t;                                            /// time
  Real & _dt;                                           /// size of the time step
  Real & _dt_old;                                       /// previous time step size
  int & _t_step;                                        /// time step (number)
  std::vector<Real> & _time_weight;                     /// Coefficients (weights) for the time discretization
  Moose::TimeSteppingScheme _time_stepping_scheme;      /// Time stepping scheme used for time discretization
  Real _time_stepping_order;                            /// The order of the time stepping scheme

  // holders
  std::vector<KernelWarehouse> _kernels;                /// Kernel storage for each thread
  std::vector<BCWarehouse> _bcs;                        /// BC storage for each thread
  std::vector<StabilizerWarehouse> _stabilizers;        /// Stabilizers storage for each thread
  std::vector<DiracKernelWarehouse> _dirac_kernels;     /// Dirac Kernel storage for each thread
  std::vector<DamperWarehouse> _dampers;                /// Dampers for each thread

  NumericVector<Number> * _increment_vec;               /// increment vector

  Preconditioner<Real> * _preconditioner;               /// Preconditioner

  bool _need_serialized_solution;                       /// Whether or not a copy of the residual needs to be made

  bool _need_residual_copy;                             /// Whether or not a copy of the residual needs to be made

  std::vector<NumericVector<Number> *> _vecs_to_zero_for_residual;   /// NumericVectors that will be zeroed before a residual computation

  friend class ComputeResidualThread;
  friend class ComputeJacobianThread;
  friend class ComputeDiracThread;
  friend class ComputeDampingThread;
};

#endif /* NONLINEARSYSTEM_H */
